schema_url = "http://json-schema.org/draft-07/schema"


platformProperties = {
    "architecture": {"type": "string"},
    "os": {"type": "string"},
    "os.version": {"type": "string"},
    "variant": {"type": "string"},
}
# TODO: add platform property type in json schema format
#   See: https://json-schema.org/understanding-json-schema/reference/object
manifestMetaProperties = {
    "mediaType": {"type": "string"},
    "platform": {"type": "object", },
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
