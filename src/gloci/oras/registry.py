import base64

import traceback

import oras.oci
import oras.defaults
import oras.auth
import oras.provider
import oras.client
import oras.utils
from oras.decorator import ensure_container
from oras.provider import Registry

from typing import Callable, Generator, List, Optional, Tuple, Union
from http.cookiejar import DefaultCookiePolicy


import logging
import jsonschema
import json
import requests

import os
import sys
import hashlib
import copy
import yaml
import uuid
from enum import Enum, auto

import gloci
from gloci.oras.crypto import calculate_sha256
from gloci.oras.defaults import annotation_signature_key, annotation_signed_string_key
from gloci.oras.schemas import (
    index as indexSchema,
    EmptyManifestMetadata,
    EmptyIndex,
    EmptyPlatform,
)


class ManifestState(Enum):
    Incomplete = auto()
    Complete = auto()
    Final = auto()


logger = logging.getLogger(__name__)
# logging.basicConfig(filename="gl-oci.log", level=logging.DEBUG)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


def attach_state(d: dict, state):
    d["image_state"] = state


def get_image_state(manifest):
    if "annotations" not in manifest:
        logger.warning("No annotations set for manifest.")
        return "UNDEFINED"
    if "image_state" not in manifest["annotations"]:
        logger.warning("No image_state set for manifest.")
        return "UNDEFINED"
    return manifest["annotations"]["image_state"]


def NewPlatform(architecture, version) -> dict:
    platform = copy.deepcopy(EmptyPlatform)
    platform["architecture"] = architecture
    platform["os.version"] = version
    return platform


def NewManifestMetadata(digest, size, annotaions, platform_data) -> dict:
    manifest_meta_data = copy.deepcopy(EmptyManifestMetadata)
    manifest_meta_data["mediaType"] = "application/vnd.oci.image.manifest.v1+json"
    manifest_meta_data["digest"] = digest
    manifest_meta_data["size"] = size
    manifest_meta_data["annotations"] = annotaions
    manifest_meta_data["platform"] = platform_data
    manifest_meta_data["artifactType"] = ""
    return manifest_meta_data


def NewIndex() -> dict:
    return copy.deepcopy(EmptyIndex)


def _check_if_manifest_exists(index, manifest_meta):
    if index is None:
        return False

    if index["manifests"] is None:
        return False

    for manifest in index["manifests"]:
        if manifest == manifest_meta:
            return True

    return False


def create_config_from_dict(conf: dict, annotations: dict):
    """
    Write a new OCI configuration to file, and generate oci meta data for it
    For reference see https://github.com/opencontainers/image-spec/blob/main/config.md
    annotations, mediatrype, size, digest are not part of digest and size calculation,
    and therefore must be attached to the output dict and not written to the file.

    :param conf: dict with custom configuration (the payload of the configuration)
    :param annotations: dict with custom annotations to be attached to metadata part of config

    """
    config_path = os.path.join(os.path.curdir, str(uuid.uuid4()))
    with open(config_path, "w") as fp:
        json.dump(conf, fp)
    conf["annotations"] = annotations
    conf["mediaType"] = oras.defaults.unknown_config_media_type
    conf["size"] = oras.utils.get_size(config_path)
    conf["digest"] = f"sha256:{oras.utils.get_file_hash(config_path)}"
    return conf, config_path


class GlociRegistry(Registry):
    def __init__(
        self,
        registry_url,
        username=None,
        token=None,
        insecure=False,
        config_path=None,
        private_key=None,
        public_key=None,
    ):
        super().__init__(auth_backend="token", insecure=insecure)
        self.registry_url = registry_url
        self.config_path = config_path
        self.private_key_path = private_key
        self.public_key_path = public_key
        if not token:
            logger.error("No Token provided")
        else:
            self.token = base64.b64encode(token.encode("utf-8")).decode("utf-8")
            self.auth.set_token_auth(self.token)

    @ensure_container
    def get_manifest_json(self, container, allowed_media_type=None):
        if not allowed_media_type:
            default_image_index_media_type = (
                "application/vnd.oci.image.manifest.v1+json"
            )
            allowed_media_type = [default_image_index_media_type]
        logger.debug("get manifest")
        # self.load_configs(container)
        headers = {"Accept": ";".join(allowed_media_type)}
        headers.update(self.headers)
        get_manifest = f"{self.prefix}://{container.manifest_url()}"
        response = self.do_request(get_manifest, "GET", headers=headers)
        self._check_200_response(response)
        return response

    @ensure_container
    def get_manifest_size(self, container, allowed_media_type=None):
        response = self.get_manifest_json(container, allowed_media_type)
        if response is None:
            return 0
        return len(response.content)

    @ensure_container
    def get_digest(self, container, allowed_media_type=None):
        response = self.get_manifest_json(container, allowed_media_type)
        if response is None:
            return ""
        return f"sha256:{hashlib.sha256(response.content).hexdigest()}"

    @ensure_container
    def get_index(self, container, allowed_media_type=None):
        """
        Returns the manifest for a cname+arch combination of a container
        Will return None if no result was found

        TODO: refactor: use get_manifest_json and call it with index mediatype.
        """
        if not allowed_media_type:
            default_image_index_media_type = "application/vnd.oci.image.index.v1+json"
            allowed_media_type = [default_image_index_media_type]

        headers = {"Accept": ";".join(allowed_media_type)}
        manifest_url = f"{self.prefix}://{container.manifest_url()}"
        response = self.do_request(manifest_url, "GET", headers=headers)
        try:
            self._check_200_response(response)
            index = response.json()
            return index

        except ValueError:
            logger.debug("Index not found")
            return NewIndex()

    @ensure_container
    def get_manifest_meta_data_by_cname(
        self, container, cname, version, arch, allowed_media_type=None
    ):
        """
        Returns the manifest for a cname+arch combination of a container
        Will return None if no result was found
        """
        index = self.get_index(container, allowed_media_type)

        if "manifests" not in index:
            logger.debug("Index is empty")
            return None

        for manifest_meta in index["manifests"]:
            if "annotations" not in manifest_meta:
                logger.debug("Manifest annotations was none, which is invalid")
                return None

            if "cname" not in manifest_meta["annotations"]:
                logger.debug("cname annotation was none, which is invalid")
                return None

            if "architecture" not in manifest_meta["annotations"]:
                logger.debug("architecture annotation was none, which is invalid")
                return None

            if "platform" not in manifest_meta:
                logger.debug("platform data was none, which is invalid")
                return None
            if (
                manifest_meta["annotations"]["cname"] == cname
                and manifest_meta["annotations"]["architecture"] == arch
                and manifest_meta["platform"]["os.version"] == version
            ):
                return manifest_meta

        return None

    @ensure_container
    def get_manifest_by_digest(self, container, digest, allowed_media_type=None):
        if not allowed_media_type:
            default_image_manifest_media_type = (
                "application/vnd.oci.image.manifest.v1+json"
            )
            allowed_media_type = [default_image_manifest_media_type]

        manifest_url = f"{self.prefix}://{container.get_blob_url(digest)}".replace(
            "/blobs/", "/manifests/"
        )
        headers = {"Accept": ";".join(allowed_media_type)}
        response = self.do_request(manifest_url, "GET", headers=headers, stream=False)
        self._check_200_response(response)
        manifest = response.json()
        jsonschema.validate(manifest, schema=oras.schemas.manifest)
        return manifest

    @ensure_container
    def get_manifest_by_cname(
        self, container, cname, version, arch, allowed_media_type=None
    ):
        """
        Returns the manifest for a cname+arch combination of a container
        Will return None if no result was found
        """
        if not allowed_media_type:
            default_image_manifest_media_type = (
                "application/vnd.oci.image.manifest.v1+json"
            )
            allowed_media_type = [default_image_manifest_media_type]
        manifest_meta = self.get_manifest_meta_data_by_cname(
            container, cname, version, arch
        )
        if manifest_meta is None:
            logger.error(f"No manifest found for {cname}-{arch}")
            return None
        if "digest" not in manifest_meta:
            logger.error("No digest found in metadata!")
        manifest_digest = manifest_meta["digest"]
        return self.get_manifest_by_digest(
            container, manifest_digest, allowed_media_type=allowed_media_type
        )

    @ensure_container
    def update_index(self, container, old_digest, manifest_meta_data):
        """
        replaces an old manifest entry with a new manifest entry
        """
        index = self.get_index(container)

        if "manifests" not in index:
            logger.debug("Index is empty")
        updated = False
        if old_digest is not None:
            for i, manifest in enumerate(index["manifests"]):
                print(f"old_digest: {old_digest} =? {manifest['digest']}")
                if manifest["digest"] == old_digest:
                    logger.debug("Found old manifest entry")
                    index["manifests"][i] = manifest_meta_data
                    updated = True
                    break
        if not updated:
            logger.debug("Did NOT find old manifest entry")
            index["manifests"].append(manifest_meta_data)

        return index

    def change_state(self, container_name, cname, version, architecture, new_state):
        manifest_container = oras.container.Container(
            f"{container_name}-{cname}-{architecture}"
        )
        manifest = self.get_manifest_by_cname(
            manifest_container, cname, version, architecture
        )

        if "annotations" not in manifest:
            logger.warning("No annotations found in manifest, init annotations now.")
            manifest["annotations"] = {}
        attach_state(manifest["annotations"], new_state)

    def attach_layer(
        self, container_name, cname, version, architecture, file_path, media_type
    ):
        if not os.path.exists(file_path):
            logger.exit(f"{file_path} does not exist.")

        checksum_sha256 = calculate_sha256(file_path)
        container = oras.container.Container(container_name)
        manifest_container = oras.container.Container(
            f"{container_name}-{cname}-{architecture}"
        )

        manifest = self.get_manifest_by_cname(container, cname, version, architecture)
        cur_state = get_image_state(manifest)
        if cur_state == "SIGNED":
            logger.exit("Manifest is already signed. Manifest is read-only now")

        layer = oras.oci.NewLayer(file_path, media_type, is_dir=False)
        layer["annotations"] = {
            oras.defaults.annotation_title: os.path.basename(file_path),
        }

        self.sign_layer(
            layer, cname, version, architecture, checksum_sha256, media_type
        )

        self._check_200_response(self.upload_blob(file_path, container, layer))

        manifest["layers"].append(layer)

        logger.debug("getting digest..")
        old_manifest_digest = self.get_digest(manifest_container)
        logger.debug("uploading manifest")
        self._check_200_response(self.upload_manifest(manifest, manifest_container))

        logger.debug("getting manifest meta data..")
        new_manifest_metadata = self.get_manifest_meta_data_by_cname(
            container, cname, version, architecture
        )
        new_manifest_metadata["digest"] = self.get_digest(manifest_container)
        new_manifest_metadata["size"] = self.get_manifest_size(manifest_container)
        new_manifest_metadata["platform"] = NewPlatform(architecture, version)

        new_index = self.update_index(
            container, old_manifest_digest, new_manifest_metadata
        )
        self._check_200_response(self.upload_index(new_index, container))

        print(f"Successfully attached {file_path} to {manifest_container}")

    def sign_layer(
        self, layer, cname, version, architecture, checksum_sha256, media_type
    ):
        data_to_sign = f"version:{version}  cname:{cname} architecture:{architecture}  media_type:{media_type}  digest:{checksum_sha256}"
        signature = gloci.oras.crypto.sign_data(data_to_sign, self.private_key_path)
        layer["annotations"] = {
            annotation_signature_key: signature,
            annotation_signed_string_key: data_to_sign,
        }

    @ensure_container
    def remove_container(self, container):
        self.delete_tag(container.manifest_url())

    @ensure_container
    def status_all(self, container):
        """
        Validate if container is valid
        - all manifests require a info.yaml in the layers
        - info.yaml needs to be signed (TODO)
        - all layers listed in info.yaml must exist
        - all mediatypes of layers listed in info.yaml must be set correctly
        """
        index = self.get_index(container)

        if "manifests" not in index:
            logger.info("No manifests in index")
            return
        for manifest_meta in index["manifests"]:
            manifest_digest = manifest_meta["digest"]
            manifest = self.get_manifest_by_digest(container, manifest_digest)
            image_state = get_image_state(manifest)
            print(f"{manifest_digest}:\t{image_state}")

    def upload_index(
        self, index: dict, container: oras.container.Container
    ) -> requests.Response:
        jsonschema.validate(index, schema=indexSchema)
        headers = {
            "Content-Type": "application/vnd.oci.image.index.v1+json",
            "Content-Length": str(len(index)),
        }
        tag = container.digest or container.tag

        index_url = f"{container.registry}/v2/{container.api_prefix}/manifests/{tag}"
        print(index)
        response = self.do_request(
            f"{self.prefix}://{index_url}",  # noqa
            "PUT",
            headers=headers,
            json=index,
        )
        logger.debug(response.content)
        return response

    def init_index(self, container):
        """
        Ensures an oci index exists for the container
        """
        image_index = self.get_index(
            container, allowed_media_type="application/vnd.oci.image.index.v1+json"
        )

        if image_index is None:
            logger.debug("Initializing new Index")
            image_index = NewIndex()
            jsonschema.validate(image_index, schema=indexSchema)
            logger.debug("Index Validated")
        else:
            logger.debug("Image Index does exist, using existing image index")
        return image_index

    def push_image_manifest(
        self, container_name, architecture, cname, version, info_yaml
    ):
        """
        creates and pushes an image manifest
        """
        container = oras.container.Container(container_name)
        if info_yaml is None:
            raise ValueError("error: info_yaml is none")
        with open(info_yaml, "r") as f:
            info_data = yaml.safe_load(f)
            base_path = os.path.join(os.path.dirname(info_yaml))

        # logger.debug("initilializing index..")
        # self.init_index(container)
        # logger.debug("done initializing index.")

        manifest_image = oras.oci.NewManifest()
        total_size = 0

        for artifact in info_data["oci_artifacts"]:
            file_name = artifact["file_name"]
            media_type = artifact["media_type"]
            annotations = artifact["annotations"]

            file_path = os.path.join(base_path, artifact["file_name"])

            checksum_sha256 = calculate_sha256(file_path)

            if not os.path.exists(file_path):
                logger.error(f"{file_path} does not exist.")
                continue

            cleanup_blob = False
            if os.path.isdir(file_path):
                file_path = oras.utils.make_targz(file_path)
                cleanup_blob = True

            layer = oras.oci.NewLayer(file_path, media_type, is_dir=cleanup_blob)
            total_size += int(layer["size"])

            layer["annotations"] = {
                oras.defaults.annotation_title: file_name,
                "application/vnd.gardenlinux.image.checksum.sha256": checksum_sha256,
            }
            self.sign_layer(
                layer, cname, version, architecture, checksum_sha256, media_type
            )
            if annotations:
                layer["annotations"].update(annotations)

            manifest_image["layers"].append(layer)

            logger.debug("Uploading blob..")
            response = self.upload_blob(file_path, container, layer)
            logger.debug("Checking response after uploading blob..")
            self._check_200_response(response)
            if cleanup_blob and os.path.exists(file_path):
                os.remove(file_path)

        layer = oras.oci.NewLayer(
            info_yaml, "application/vnd.gardenlinux.metadata.info", is_dir=False
        )
        total_size += int(layer["size"])
        manifest_image["layers"].append(layer)
        manifest_image["annotations"] = {}
        manifest_image["annotations"]["version"] = version
        manifest_image["annotations"]["cname"] = cname
        manifest_image["annotations"]["architecture"] = architecture
        attach_state(manifest_image["annotations"], "UNTESTED")

        if container is None:
            raise ValueError("error: container is none")
        if layer is None:
            raise ValueError("error: layer is none")
        response = self.upload_blob(info_yaml, container, layer)
        self._check_200_response(response)

        config_annotations = {"cname": cname, "architecture": architecture}
        conf, config_file = create_config_from_dict(dict(), config_annotations)

        response = self.upload_blob(config_file, container, conf)

        os.remove(config_file)
        self._check_200_response(response)

        manifest_image["config"] = conf

        manifest_container = oras.container.Container(
            f"{container_name}-{cname}-{architecture}"
        )

        self._check_200_response(
            self.upload_manifest(manifest_image, manifest_container)
        )

        # attach Manifest to oci-index
        metadata_annotations = {"cname": cname, "architecture": architecture}
        attach_state(metadata_annotations, "UNTESTED")
        manifest_digest = self.get_digest(manifest_container)
        manifest_index_metadata = NewManifestMetadata(
            manifest_digest,
            self.get_manifest_size(manifest_container),
            metadata_annotations,
            NewPlatform(architecture, version),
        )

        old_manifest_meta_data = self.get_manifest_meta_data_by_cname(
            container, cname, version, architecture
        )
        if old_manifest_meta_data is not None:
            new_index = self.update_index(
                container, old_manifest_meta_data["digest"], manifest_index_metadata
            )
            print(new_index)
        else:
            new_index = self.update_index(container, None, manifest_index_metadata)
            print(new_index)

        self._check_200_response(self.upload_index(new_index, container))

        print(f"Successfully pushed {container}")
        return response
