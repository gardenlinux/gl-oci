# gl-oci: Tool to create OCI artefacts and publish OCI


**gl-oci** is a command line tool that can be used to create OCI artefacts 
for arbitrary data. 
* Create manifests based on data and mediatypes defined in a simple  yaml files
* Attach layers and annotations to existing manifests

## Setup

```commandline
make create_venv
source .venv/bin/activate

poetry install
poetry build
poetry run cli --help
```

 
Currently, this gl-oci tool is under development - but it is planed to properly package it
and publish it to pypi. 

For now, you need to check out this repo and run it as described above.

## Demo 
```
make create_venv
source .venv/bin/activate
make install_deps
make example_manifest

```
