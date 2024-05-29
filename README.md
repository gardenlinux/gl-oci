# gl-oci: Tool to create OCI artefacts and publish OCI

![example workflow](https://github.com/gardenlinux/gl-oci/actions/workflows/go.yml/badge.svg)

**gl-oci** is a command line tool that implements functions to manage garden linux OCI artefacts. 

Features:
- initialize components, such as the oci-index
- incrementally add content to an existing OCI 
- utilizes ORAS to ensure OCI-spec compliance 



## Build and install

```
go build
go install

```


## Usage

```
gl-oci help
```
