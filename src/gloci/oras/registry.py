import oras.oci
import oras.defaults
import oras.provider
import oras.oci
import oras.defaults
import oras.provider
import oras.client
from oras.decorator import ensure_container
import oras.utils
import os
import sys
import yaml

from oras.logger import setup_logger, logger
setup_logger(quiet=False, debug=True)

class Registry(oras.provider.Registry):
    def __init__(self, registry_url, config_path=None):
        super().__init__(insecure=True)
        self.registry_url = registry_url
        self.config_path = config_path

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
    def push(self, container, info_yaml):
        """
        Given a dict of layers (paths and corresponding mediaType) push.
        """

        with open(info_yaml, 'r') as f:
            info_data = yaml.safe_load(f)
            base_path = os.path.join(os.path.dirname(info_yaml))
        conf, config_file = oras.oci.ManifestConfig()

        # Prepare a new manifest
        manifest = oras.oci.NewManifest()

        # First Layer is garden linux info.yaml
        layer = oras.oci.NewLayer(info_yaml, "application/vnd.gardenlinux.metadata.info", is_dir=False)
        manifest["layers"].append(layer)
        response = self.upload_blob(info_yaml, container, layer)
        self._check_200_response(response)

        # Iterate over oci_artifacts
        for artifact in info_data['oci_artifacts']:
            file_name = artifact['file_name']
            media_type = artifact['media_type']
            annotations = artifact['annotations']

            file_path = os.path.join(base_path, artifact['file_name'])

            # File Blobs must exist
            if not os.path.exists(file_path):
                logger.exit(f"{file_path} does not exist.")

            cleanup_blob = False
            if os.path.isdir(file_path):
                file_path = oras.utils.make_targz(file_path)
                cleanup_blob = True

            # Create a new layer from the blob
            layer = oras.oci.NewLayer(file_path, media_type, is_dir=cleanup_blob)
            # annotations = annotations.get_annotations(blob)
            layer["annotations"] = {oras.defaults.annotation_title: file_name}
            # if annotations:
            #    layer["annotations"].update(annotations)


            # update the manifest with the new layer
            manifest["layers"].append(layer)


            # Upload the blob layer
            response = self.upload_blob(file_path, container, layer)
            self._check_200_response(response)

            # Do we need to clean up a temporary targz?
            if cleanup_blob and os.path.exists(file_path):
                os.remove(file_path)

        config_file = os.path.join(os.path.curdir, "tmp-config")
        if not os.path.exists(config_file):
            with open(config_file, 'w'): pass

        conf, _ = oras.oci.ManifestConfig(path=config_file)
        #conf["annotations"] = {}

        # Config is just another layer blob!
        response = self.upload_blob(config_file, container, conf)
        self._check_200_response(response)

        # Final upload of the manifest
        manifest["config"] = conf

        print(manifest)

        self._check_200_response(self.upload_manifest(manifest, container))
        print(f"Successfully pushed {container}")
        return response