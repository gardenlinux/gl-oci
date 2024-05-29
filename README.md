# gl-oci: Tool to create OCI artefacts and publish OCI

![example workflow](https://github.com/gardenlinux/gl-oci/actions/workflows/go.yml/badge.svg)

**gl-oci** is a command line tool that implements functions to manage garden linux OCI artefacts. 

Features:
- bootstrap OCI
- incrementally add content to OCI 
- build-in OCM support


## Build and install

```
go build
go install

```


## Usage

```
gl-oci help
```


## Related Projects
- https://github.com/ironcore-dev/ironcore-image
  - similiar use case of creating images and pushing images to a registry
  - key difference of gl-oci
      - ocm integration
      - API designed for Garden Linux use case: appending to existing images, so that multiple timely independent pipeline steps of Garden Linux can attach/append output to an existing OCI
