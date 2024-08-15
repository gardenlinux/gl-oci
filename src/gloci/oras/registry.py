import base64
import copy
import hashlib
import json
import logging
import os
import sys
import uuid
from enum import Enum, auto
from typing import Optional, Tuple
from parse_features_lib.parse_features import read_feature_files

import jsonschema
import oras.auth
import oras.client
import oras.defaults
import oras.oci
import oras.provider
import oras.utils
import requests
import yaml
from oras.container import Container as OrasContainer
from oras.decorator import ensure_container
from oras.provider import Registry
from oras.schemas import manifest as oras_manifest_schema

from gloci.oras.crypto import (
    calculate_sha256,
    sign_data,
    verify_sha256,
    verify_signature,
)
from gloci.oras.defaults import annotation_signature_key, annotation_signed_string_key
from gloci.oras.schemas import EmptyIndex, EmptyManifestMetadata, EmptyPlatform
from gloci.oras.schemas import index as indexSchema


class ManifestState(Enum):
    Incomplete = auto()
    Complete = auto()
    Final = auto()


logger = logging.getLogger(__name__)
# logging.basicConfig(filename="gl-oci.log", level=logging.DEBUG)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


def attach_state(d: dict, state: str):
    d["image_state"] = state


def get_image_state(manifest: dict) -> str:
    if "annotations" not in manifest:
        logger.warning("No annotations set for manifest.")
        return "UNDEFINED"
    if "image_state" not in manifest["annotations"]:
        logger.warning("No image_state set for manifest.")
        return "UNDEFINED"
    return manifest["annotations"]["image_state"]


def NewPlatform(architecture: str, version: str) -> dict:
    platform = copy.deepcopy(EmptyPlatform)
    platform["architecture"] = architecture
    platform["os.version"] = version
    return platform


def NewManifestMetadata(
    digest: str, size: int, annotaions: dict, platform_data: dict
) -> dict:
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


def create_config_from_dict(conf: dict, annotations: dict) -> Tuple[dict, str]:
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


def construct_manifest_entry_signed_data_string(
    cname: str, version: str, new_manifest_metadata: dict, architecture: str
) -> str:
    data_to_sign = f"versio:{version}  cname{cname}  architecture:{architecture}  manifest-size:{new_manifest_metadata['size']}  manifest-digest:{new_manifest_metadata['digest']}"
    return data_to_sign


def construct_layer_signed_data_string(
    cname: str, version: str, architecture: str, media_type: str, checksum_sha256: str
) -> str:
    data_to_sign = f"version:{version}  cname:{cname} architecture:{architecture}  media_type:{media_type}  digest:{checksum_sha256}"
    return data_to_sign


class GlociRegistry(Registry):
    def __init__(
        self,
        container_name: str,
        token: Optional[str] = None,
        insecure: bool = False,
        private_key: Optional[str] = None,
        public_key: Optional[str] = None,
        config_path: Optional[str] = None,
    ):
        super().__init__(auth_backend="token", insecure=insecure)
        self.container = OrasContainer(container_name)
        self.container_name = container_name
        self.registry_url = self.container.registry
        self.config_path = config_path
        self.private_key_path = private_key
        self.public_key_path = public_key
        if not token:
            logger.error("No Token provided")
        else:
            self.token = base64.b64encode(token.encode("utf-8")).decode("utf-8")
            self.auth.set_token_auth(self.token)

    @ensure_container
    def get_manifest_json(
        self, container: OrasContainer, allowed_media_type: Optional[list[str]] = None
    ):
        if not allowed_media_type:
            default_image_index_media_type = (
                "application/vnd.oci.image.manifest.v1+json"
            )
            allowed_media_type = [default_image_index_media_type]
        # self.load_configs(container)
        headers = {"Accept": ";".join(allowed_media_type)}
        headers.update(self.headers)
        get_manifest = f"{self.prefix}://{container.manifest_url()}"
        response = self.do_request(get_manifest, "GET", headers=headers)
        self._check_200_response(response)
        self.verify_manifest_signature(response.json())
        return response

    @ensure_container
    def get_manifest_size(
        self, container: OrasContainer, allowed_media_type: Optional[list[str]] = None
    ):
        response = self.get_manifest_json(container, allowed_media_type)
        if response is None:
            return 0
        return len(response.content)

    @ensure_container
    def get_digest(
        self, container: OrasContainer, allowed_media_type: Optional[list[str]] = None
    ):
        response = self.get_manifest_json(container, allowed_media_type)
        if response is None:
            return ""
        return f"sha256:{hashlib.sha256(response.content).hexdigest()}"

    def get_index(self, allowed_media_type: Optional[list[str]] = None):
        """
        Returns the manifest for a cname+arch combination of a container
        Will return None if no result was found

        TODO: refactor: use get_manifest_json and call it with index mediatype.
        """
        if not allowed_media_type:
            default_image_index_media_type = "application/vnd.oci.image.index.v1+json"
            allowed_media_type = [default_image_index_media_type]

        headers = {"Accept": ";".join(allowed_media_type)}
        manifest_url = f"{self.prefix}://{self.container.manifest_url()}"
        response = self.do_request(manifest_url, "GET", headers=headers)
        try:
            self._check_200_response(response)
            index = response.json()
            return index

        except ValueError:
            logger.debug("Index not found, creating new Index!")
            return NewIndex()

    @ensure_container
    def get_manifest_meta_data_by_cname(
        self,
        container: OrasContainer,
        cname: str,
        version: str,
        arch: str,
        allowed_media_type: Optional[list[str]] = None,
    ):
        """
        Returns the manifest for a cname+arch combination of a container
        Will return None if no result was found
        """
        index = self.get_index(allowed_media_type=allowed_media_type)

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
                self.verify_manifest_meta_signature(manifest_meta)
                return manifest_meta

        return None

    @ensure_container
    def get_manifest_by_digest(
        self,
        container: OrasContainer,
        digest: str,
        allowed_media_type: Optional[list[str]] = None,
    ):
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
        verify_sha256(digest, response.content)
        self.verify_manifest_signature(manifest)
        jsonschema.validate(manifest, schema=oras_manifest_schema)
        return manifest

    @ensure_container
    def get_manifest_by_cname(
        self,
        container: OrasContainer,
        cname: str,
        version: str,
        arch: str,
        allowed_media_type: Optional[list[str]] = None,
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

    def update_index(self, old_digest: Optional[str], manifest_meta_data: dict):
        """
        replaces an old manifest entry with a new manifest entry
        """
        index = self.get_index()

        if "manifests" not in index:
            logger.debug("Index is empty")
        updated = False
        if old_digest is not None:
            for i, manifest in enumerate(index["manifests"]):
                if manifest["digest"] == old_digest:
                    logger.debug("Found old manifest entry")
                    index["manifests"][i] = manifest_meta_data
                    updated = True
                    break
        if not updated:
            logger.debug("Did NOT find old manifest entry")
            index["manifests"].append(manifest_meta_data)

        return index

    def change_state(self, cname: str, version: str, architecture: str, new_state: str):
        manifest_container = OrasContainer(
            f"{self.container_name}-{cname}-{architecture}"
        )
        manifest = self.get_manifest_by_cname(
            manifest_container, cname, version, architecture
        )

        if "annotations" not in manifest:
            logger.warning("No annotations found in manifest, init annotations now.")
            manifest["annotations"] = {}
        attach_state(manifest["annotations"], new_state)

    def attach_layer(
        self,
        cname: str,
        version: str,
        architecture: str,
        file_path: str,
        media_type: str,
    ):
        if not os.path.exists(file_path):
            exit(f"{file_path} does not exist.")

        manifest_container = OrasContainer(
            f"{self.container_name}-{cname}-{architecture}"
        )

        manifest = self.get_manifest_by_cname(
            self.container, cname, version, architecture
        )

        self.verify_manifest_signature(manifest)

        layer = self.create_layer(file_path, cname, version, architecture, media_type)
        self._check_200_response(self.upload_blob(file_path, self.container, layer))

        manifest["layers"].append(layer)

        old_manifest_digest = self.get_digest(manifest_container)
        self._check_200_response(self.upload_manifest(manifest, manifest_container))

        new_manifest_metadata = self.get_manifest_meta_data_by_cname(
            self.container, cname, version, architecture
        )
        new_manifest_metadata["digest"] = self.get_digest(manifest_container)
        new_manifest_metadata["size"] = self.get_manifest_size(manifest_container)
        new_manifest_metadata["platform"] = NewPlatform(architecture, version)

        self.sign_manifest_entry(new_manifest_metadata, version, architecture, cname)
        new_index = self.update_index(old_manifest_digest, new_manifest_metadata)
        self._check_200_response(self.upload_index(new_index))

        print(f"Successfully attached {file_path} to {manifest_container}")

    def sign_manifest_entry(
        self, new_manifest_metadata: dict, version: str, architecture: str, cname: str
    ):
        data_to_sign = construct_manifest_entry_signed_data_string(
            cname, version, new_manifest_metadata, architecture
        )
        if not self.private_key_path:
            raise ValueError(
                "No Private Key was given. Can not sign, but signing was required."
            )
        signature = sign_data(data_to_sign, self.private_key_path)
        new_manifest_metadata["annotations"].update(
            {
                annotation_signature_key: signature,
                annotation_signed_string_key: data_to_sign,
            }
        )

    def sign_layer(
        self,
        layer: dict,
        cname: str,
        version: str,
        architecture: str,
        checksum_sha256: str,
        media_type: str,
    ):
        if self.private_key_path is None:
            raise ValueError(
                "No Private Key was given. Can not sign, but signing was required."
            )

        data_to_sign = construct_layer_signed_data_string(
            cname, version, architecture, media_type, checksum_sha256
        )
        signature = sign_data(data_to_sign, self.private_key_path)
        layer["annotations"].update(
            {
                annotation_signature_key: signature,
                annotation_signed_string_key: data_to_sign,
            }
        )

    def verify_manifest_meta_signature(self, manifest_meta: dict):
        if "annotations" not in manifest_meta:
            raise ValueError("manifest does not contain annotations")
        if annotation_signature_key not in manifest_meta["annotations"]:
            raise ValueError("manifest is not signed")
        if annotation_signed_string_key not in manifest_meta["annotations"]:
            raise ValueError("manifest is not signed")
        signature = manifest_meta["annotations"][annotation_signature_key]
        signed_data = manifest_meta["annotations"][annotation_signed_string_key]
        cname = manifest_meta["annotations"]["cname"]
        version = manifest_meta["platform"]["os.version"]
        architecture = manifest_meta["annotations"]["architecture"]
        signed_data_expected = construct_manifest_entry_signed_data_string(
            cname, version, manifest_meta, architecture
        )
        if signed_data_expected != signed_data:
            raise ValueError(
                f"Signed data does not match expected signed data.\n{signed_data} != {signed_data_expected}"
            )
        logger.debug(f"verifying signature with public key {self.public_key_path}")
        if self.public_key_path is None:
            raise ValueError(
                "No Public Key was given. Can not verify signature, but verification of signature was required."
            )
        verify_signature(signed_data, signature, self.public_key_path)

    def verify_manifest_signature(self, manifest: dict):
        if "layers" not in manifest:
            raise ValueError("manifest does not contain layers")
        if "annotations" not in manifest:
            raise ValueError("manifest does not contain annotations")

        cname = manifest["annotations"]["cname"]
        version = manifest["annotations"]["version"]
        architecture = manifest["annotations"]["architecture"]
        for layer in manifest["layers"]:
            if "annotations" not in layer:
                raise ValueError(f"layer does not contain annotations. layer: {layer}")
            if annotation_signature_key not in layer["annotations"]:
                raise ValueError(f"layer is not signed. layer: {layer}")
            if annotation_signed_string_key not in layer["annotations"]:
                raise ValueError(f"layer is not signed. layer: {layer}")
            media_type = layer["mediaType"]
            checksum_sha256 = layer["annotations"][
                "application/vnd.gardenlinux.image.checksum.sha256"
            ]
            signature = layer["annotations"][annotation_signature_key]
            signed_data = layer["annotations"][annotation_signed_string_key]
            signed_data_expected = construct_layer_signed_data_string(
                cname, version, architecture, media_type, checksum_sha256
            )
            if signed_data_expected != signed_data:
                raise ValueError(
                    f"Signed data does not match expected signed data. {signed_data} != {signed_data_expected}"
                )
            if not self.public_key_path:
                raise ValueError(
                    "No public key was given, but verification of signature was required"
                )
            verify_signature(signed_data, signature, self.public_key_path)

    @ensure_container
    def remove_container(self, container: OrasContainer):
        self.delete_tag(container.manifest_url())

    def status_all(self):
        """
        Validate if container is valid
        - all manifests require a info.yaml in the layers
        - info.yaml needs to be signed (TODO)
        - all layers listed in info.yaml must exist
        - all mediatypes of layers listed in info.yaml must be set correctly
        """
        index = self.get_index()

        if "manifests" not in index:
            logger.info("No manifests in index")
            return
        for manifest_meta in index["manifests"]:
            manifest_digest = manifest_meta["digest"]
            manifest = self.get_manifest_by_digest(self.container, manifest_digest)
            image_state = get_image_state(manifest)
            print(f"{manifest_digest}:\t{image_state}")

    def upload_index(self, index: dict) -> requests.Response:
        jsonschema.validate(index, schema=indexSchema)
        headers = {
            "Content-Type": "application/vnd.oci.image.index.v1+json",
            "Content-Length": str(len(index)),
        }
        tag = self.container.digest or self.container.tag

        index_url = (
            f"{self.container.registry}/v2/{self.container.api_prefix}/manifests/{tag}"
        )
        response = self.do_request(
            f"{self.prefix}://{index_url}",  # noqa
            "PUT",
            headers=headers,
            json=index,
        )
        return response

    def push_image_manifest(
        self, architecture: str, cname: str, version: str, info_yaml: str
    ):
        """
        creates and pushes an image manifest
        """
        # container = OrasContainer(container_name)
        with open(info_yaml, "r") as f:
            info_data = yaml.safe_load(f)
            base_path = os.path.join(os.path.dirname(info_yaml))

        manifest_image = oras.oci.NewManifest()
        total_size = 0

        for artifact in info_data["oci_artifacts"]:
            annotations_input = artifact["annotations"]
            media_type = artifact["media_type"]
            file_path = os.path.join(base_path, artifact["file_name"])

            if not os.path.exists(file_path):
                logger.error(f"{file_path} does not exist.")
                continue

            cleanup_blob = False
            if os.path.isdir(file_path):
                file_path = oras.utils.make_targz(file_path)
                cleanup_blob = True

            layer = self.create_layer(
                file_path, cname, version, architecture, media_type
            )
            total_size += int(layer["size"])

            if annotations_input:
                layer["annotations"].update(annotations_input)
            manifest_image["layers"].append(layer)

            response = self.upload_blob(file_path, self.container, layer)
            self._check_200_response(response)
            if cleanup_blob and os.path.exists(file_path):
                os.remove(file_path)
        layer = self.create_layer(
            info_yaml,
            cname,
            version,
            architecture,
            "application/io.gardenlinux.oci.info-yaml",
        )
        total_size += int(layer["size"])
        manifest_image["layers"].append(layer)
        manifest_image["annotations"] = {}
        manifest_image["annotations"]["version"] = version
        manifest_image["annotations"]["cname"] = cname
        manifest_image["annotations"]["architecture"] = architecture
        attach_state(manifest_image["annotations"], "UNTESTED")

        if layer is None:
            raise ValueError("error: layer is none")
        response = self.upload_blob(info_yaml, self.container, layer)
        self._check_200_response(response)

        config_annotations = {"cname": cname, "architecture": architecture}
        conf, config_file = create_config_from_dict(dict(), config_annotations)

        response = self.upload_blob(config_file, self.container, conf)

        os.remove(config_file)
        self._check_200_response(response)

        manifest_image["config"] = conf

        manifest_container = OrasContainer(
            f"{self.container_name}-{cname}-{architecture}"
        )

        self._check_200_response(
            self.upload_manifest(manifest_image, manifest_container)
        )

        metadata_annotations = {"cname": cname, "architecture": architecture}
        attach_state(metadata_annotations, "UNTESTED")
        manifest_digest = self.get_digest(manifest_container)
        manifest_index_metadata = NewManifestMetadata(
            manifest_digest,
            self.get_manifest_size(manifest_container),
            metadata_annotations,
            NewPlatform(architecture, version),
        )
        self.sign_manifest_entry(manifest_index_metadata, version, architecture, cname)

        old_manifest_meta_data = self.get_manifest_meta_data_by_cname(
            self.container, cname, version, architecture
        )
        if old_manifest_meta_data is not None:
            new_index = self.update_index(
                old_manifest_meta_data["digest"], manifest_index_metadata
            )
        else:
            new_index = self.update_index(None, manifest_index_metadata)

        self._check_200_response(self.upload_index(new_index))

        print(f"Successfully pushed {self.container}")
        return response

    def create_layer(
        self,
        file_path: str,
        cname: str,
        version: str,
        architecture: str,
        media_type: str,
    ):
        checksum_sha256 = calculate_sha256(file_path)
        layer = oras.oci.NewLayer(file_path, media_type, is_dir=False)
        layer["annotations"] = {
            oras.defaults.annotation_title: file_path,
            "application/vnd.gardenlinux.image.checksum.sha256": checksum_sha256,
        }
        self.sign_layer(
            layer, cname, version, architecture, checksum_sha256, media_type
        )
        return layer
