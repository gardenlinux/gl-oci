# for reference:
#   https://json-schema.org/understanding-json-schema/reference/object

schema_url = "http://json-schema.org/draft-07/schema"

platformProperties = {
    "architecture": {"type": "string"},
    "os": {"type": "string"},
    "os.version": {"type": "string"},
    "variant": {"type": "string"},
}

manifestMetaProperties = {
    "mediaType": {"type": "string"},
    "platform": {"type": "object", "properties": platformProperties},
}

indexProperties = {
    "schemaVersion": {"type": "number"},
    "mediaType": {"type": "string"},
    "subject": {"type": ["null", "object"]},
    "manifests": {"type": "array", "items": manifestMetaProperties},
    "annotations": {"type": ["object", "null", "array"]},
}


index = {
    "$schema": schema_url,
    "title": "Index Schema",
    "type": "object",
    "required": [
        "schemaVersion",
        "manifests",
    ],
    "properties": indexProperties,
    "additionalProperties": True,
}

EmptyPlatform = {
    "architecture": "",
    "os": "gardenlinux",
    "os.version": "experimental",
}

EmptyManifestMetadata = {
    "mediaType": "application/vnd.oci.image.manifest.v1+json",
    "digest": "",
    "size": 0,
    "annotations": {},
    "artifactType": "",
}

EmptyIndex = {
    "schemaVersion": 2,
    "mediaType": "application/vnd.oci.image.index.v1+json",
    "manifests": [],
    "annotations": {},
}
