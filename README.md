![poetry build](https://github.com/gardenlinux/gl-oci/actions/workflows/build.yml/badge.svg)
![Black Lint](https://github.com/gardenlinux/gl-oci/actions/workflows/black.yml/badge.svg)
# gl-oci: Tool to create OCI artefacts and publish OCI
# 


**gl-oci** is a command line tool that can be used to create OCI artefacts 
for arbitrary data. 
* Create manifests based on data and mediatypes defined in a simple  yaml files
* Attach layers and annotations to existing manifests
* Status System (incomplete, complete, final) for all oci manifests 

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


## Workflow

```
- Build Pipeline builds Garden linux image artifacts
- Create manifest based on Garden Linux info.yaml
    - Create layers for all present image artifacts
    - Create layer for info.yaml containing maintainer specific 
    - set status of manifest

for each additional Pipeline Step that produces additional artifacts:
    - run pipeline
    - attach additional layers

- finalize manifest
    - set status
    - sign manifest
``` 

Incomplete manifests are uploaded to oci-registry with respective status.
Final state can be verified by:
- reading status annotation
- verifying that signature exists and verifying if signature is valid


## Demo 
```
# Prepare environment once
make create_venv
source .venv/bin/activate
make install_deps

# run example that creates an image and pushes it to zot oci
make serve-oci
make example
```
