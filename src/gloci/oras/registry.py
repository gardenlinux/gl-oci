import pprint

import oras.oci
import oras.defaults
import oras.provider
import oras.client
import oras.utils
from oras.decorator import ensure_container
from oras.logger import setup_logger, logger

import os
import yaml
import uuid
import re
from enum import Enum, auto

from gloci.oras.crypto import calculate_sha1, calculate_md5, calculate_sha256


class ManifestState(Enum):
    Incomplete = auto()
    Complete = auto()
    Final = auto()


setup_logger(quiet=False, debug=True)


def get_uri_for_digest(uri, digest):
    """
    Given a URI for an image, return a URI for the related digest.

    URI may be in any of the following forms:

        ghcr.io/homebrew/core/hello
        ghcr.io/homebrew/core/hello:2.10
        ghcr.io/homebrew/core/hello@sha256:ff81...47a
    """
    base_uri = re.split(r"[@:]", uri, maxsplit=1)[0]
    return f"{base_uri}@{digest}"


class Registry(oras.provider.Registry):
    def __init__(self, registry_url, config_path=None):
        super().__init__(insecure=True)
        self.registry_url = registry_url
        self.config_path = config_path

    @ensure_container
    def get_image_index(self, container, allowed_media_type=None):
        """
        Get an image index as a manifest.

        This is basically Registry.get_manifest with the following changes

        - different default allowed_media_type
        - no JSON schema validation
        """
        if not allowed_media_type:
            default_image_index_media_type = "application/vnd.oci.image.index.v1+json"
            allowed_media_type = [default_image_index_media_type]

        headers = {"Accept": ";".join(allowed_media_type)}
        logger.debug("get remote manifest")
        manifest_url = f"{self.prefix}://{container.manifest_url()}"
        response = self.do_request(manifest_url, "GET", headers=headers)
        self._check_200_response(response)
        manifest = response.json()
        # this would be a good point to validate the schema of the manifest
        # jsonschema.validate(manifest, schema=...)
        return manifest

    def get_index_manifest(self, container):
        index_manifest = self.get_image_index(container)
        return index_manifest

    def attach_layer(self, container, file_path, media_type):

        # File Blobs must exist
        if not os.path.exists(file_path):
            logger.exit(f"{file_path} does not exist.")

        manifest = self.get_manifest(container)

        # Create a new layer from the blob
        layer = oras.oci.NewLayer(file_path, media_type, is_dir=False)
        # annotations = annotations.get_annotations(blob)
        layer["annotations"] = {oras.defaults.annotation_title: os.path.basename(file_path)}
        # if annotations:
        #    layer["annotations"].update(annotations)

        # update the manifest with the new layer
        manifest["layers"].append(layer)

        self._check_200_response(self.upload_manifest(manifest, container))
        print(f"Successfully attached {file_path} to {container}")


    @ensure_container
    def status_manifest(self, container, manifest_id):
        pass
    @ensure_container
    def status_all(self, container):
        """
        Validate if container is valid
        - all manifests require a info.yaml in the layers
        - info.yaml needs to be signed (TODO)
        - all layers listed in info.yaml must exist
        - all mediatypes of layers listed in info.yaml must be set correctly
        """

        manifest = self.get_manifest(container)

    @ensure_container
    def push_image_manifest(self, container, info_yaml):
        """
        creates and pushes an image manifest
        """
        logger.debug("start push image manifest") 
        assert info_yaml is not None, "error: info_yaml is None"
        with open(info_yaml, 'r') as f:
            info_data = yaml.safe_load(f)
            base_path = os.path.join(os.path.dirname(info_yaml))
        conf, config_file = oras.oci.ManifestConfig()

        logger.debug("Creating new Manifest")
        manifest_image = oras.oci.NewManifest()

        logger.debug("Create metadata info Layer")
        layer = oras.oci.NewLayer(info_yaml, "application/vnd.gardenlinux.metadata.info", is_dir=False)
        manifest_image["layers"].append(layer)

        logger.debug("Upload metadata info Layer")
        assert container is not None, "error: container is none"
        assert layer is not None, "error: layer is none"
        response = self.upload_blob(info_yaml, container, layer)

        logger.debug("Check response from upload metadata info Layer")
        self._check_200_response(response)

        missing_layer_detected = False

        logger.debug("Iterate over all artifacts specified in info yaml...")
        for artifact in info_data['oci_artifacts']:
            logger.debug("Layer Info:")
            file_name = artifact['file_name']
            media_type = artifact['media_type']
            annotations = artifact['annotations']
            logger.debug(f"\tfilename:= {file_name}")
            logger.debug(f"\tmediatype:= {media_type}")
            logger.debug(f"\tannotations:= {annotations}")

            file_path = os.path.join(base_path, artifact['file_name'])
            # File Blobs must exist
            if not os.path.exists(file_path):
                logger.info(f"{file_path} does not exist.")
                # TODO: Set Status of manifest to incomplete layers
                missing_layer_detected = True
                continue

            cleanup_blob = False
            if os.path.isdir(file_path):
                file_path = oras.utils.make_targz(file_path)
                cleanup_blob = True

            # Create a new layer from the blob
            layer = oras.oci.NewLayer(file_path, media_type, is_dir=cleanup_blob)
            # annotations = annotations.get_annotations(blob)
            checksum_sha256 = calculate_sha256(file_path)
            checksum_sha1 = calculate_sha1(file_path)
            checksum_md5 = calculate_md5(file_path)
            layer["annotations"] = {
                oras.defaults.annotation_title: file_name,
                "application/vnd.gardenlinux.image.checksum.sha256": checksum_sha256,
                "application/vnd.gardenlinux.image.checksum.sha1": checksum_md5,
                "application/vnd.gardenlinux.image.checksum.md5": checksum_md5,

            }
            if annotations:
                layer["annotations"].update(annotations)

            # update the manifest with the new layer
            manifest_image["layers"].append(layer)

            # Upload the blob layer
            response = self.upload_blob(file_path, container, layer)
            self._check_200_response(response)

            # Do we need to clean up a temporary targz?
            if cleanup_blob and os.path.exists(file_path):
                os.remove(file_path)

        config_file = os.path.join(os.path.curdir, str(uuid.uuid4()))
        if not os.path.exists(config_file):
            with open(config_file, 'w'):
                pass

        conf, _ = oras.oci.ManifestConfig(path=config_file)
        conf["annotations"] = {}

        # Config is just another layer blob!
        response = self.upload_blob(config_file, container, conf)
        self._check_200_response(response)

        os.remove(config_file)
        # Final upload of the manifest
        manifest_image["config"] = conf

        self._check_200_response(self.upload_manifest(manifest_image, container))
        print(f"Successfully pushed {container}")
        return response
