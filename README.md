# gl-oci: Tool to create OCI artefacts and publish OCI
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/gardenlinux/gl-oci/go)

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
