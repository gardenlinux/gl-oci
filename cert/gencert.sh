#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
CERT_NAME="$SCRIPT_DIR/oci-sign"


openssl req -x509 -newkey rsa -pkeyopt rsa_keygen_bits:4096  -days 3650 -nodes -keyout $CERT_NAME.key -out $CERT_NAME.crt -subj "/CN=Garden Linux test signing key for oci"

