import re
import json
import os


def write_dict_to_json_file(input, output_path):
    if os.path.exists(output_path):
        raise ValueError(f"{output_path} already exists")
    with open(output_path, "w") as fp:
        json.dump(input, fp)


def get_uri_for_digest(uri, digest):
    """
    Given a URI for an image, return a URI for the related digest.

    URI may be in any of the following forms:

        ghcr.io/homebrew/core/hello
        ghcr.io/homebrew/core/hello:2.10
        ghcr.io/homebrew/core/hello@sha256:ff81...47a
    """
    base_uri = re.split(r"[@:]", uri, maxsplit=1)[0]
    return f"{base_uri}@{digest}"
