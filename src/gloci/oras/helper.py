import oras.client
import os
import oras.oci
import oras.defaults


def create_layer(list_of_files):
    layers = []
    for blob in list_of_files:
        layer = oras.oci.NewLayer(blob, is_dir=False, media_type="org.dinosaur.tools.blobish")

        # This is important so oras clients can derive the relative name you want to download to
        # Using basename assumes a flat directory of files - it doesn't have to be.
        # You can add more annotations here!
        layer["annotations"] = {oras.defaults.annotation_title: os.path.basename(blob)}
        layers.append(layer)
    return layers


def create_manifest(list_of_files):
    conf, config_file = oras.oci.ManifestConfig()

    layers = create_layer(list_of_files)
    # Prepare a new manifest
    manifest = oras.oci.NewManifest()

    # update the manifest with layers
    manifest["layers"] = layers

    # Note that you can add annotations to the manifest too
    manifest['annotations'] = {'org.dinosaur.tool.food': 'avocado'}

    # Add your previously created config to it!
    manifest["config"] = conf

    return manifest

def upload_manifest(manifest):
   pass
