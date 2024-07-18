#!/bin/bash

OCI_URL=$1
TOKEN_FILE="$HOME/.GH_TOKEN"

if [ -f "$TOKEN_FILE" ]; then
    TOKEN=$(cat "$TOKEN_FILE")
else
    echo "You need a GitHub Token in ~/.GH_TOKEN"
    exit 1
fi
GHCR_TOKEN=$(echo "$TOKEN" | base64)


BASE_URL=$(echo "$OCI_URL" | awk -F'/' '{print $1}')
echo "BASE_URL: $BASE_URL"

USER_IMAGE=$(echo "$OCI_URL" | cut -d'/' -f2-)

echo "USER_IMAGE: $USER_IMAGE"

if [[ "$USER_IMAGE" == *"@"* ]]; then
    DIGEST=$(echo "$USER_IMAGE" | awk -F'@' '{print $2}')
    USER_IMAGE=$(echo "$USER_IMAGE" | awk -F'@' '{print $1}')
elif [[ "$USER_IMAGE" == *":"* ]]; then
    DIGEST=$(echo "$USER_IMAGE" | awk -F':' '{print $2}')
    USER_IMAGE=$(echo "$USER_IMAGE" | awk -F':' '{print $1}')
else
    echo "URL does not contain a digest"
    exit 1
fi
echo "DIGEST: $DIGEST"

USER=$(echo "$USER_IMAGE" | awk -F'/' '{print $1}')
echo "USER: $USER"
IMAGE=$(echo "$USER_IMAGE" | cut -d'/' -f2- | awk -F'[@:]' '{print $1}')
echo "IMAGE: $IMAGE"


QUERY_URL="https://${BASE_URL}/v2/${USER}/${IMAGE}/manifests/${DIGEST}"

echo "OCI-Index for $QUERY_URL"
#RESPONSE=$(curl -s -w "\n%{http_code}" -H "Authorization: Bearer ${TOKEN}" "$QUERY_URL")
RESPONSE=$(curl -s -L -X GET -w "\n%{http_code}" -H "Accept: application/vnd.oci.image.index.v1+json"  -H "Authorization: Bearer ${GHCR_TOKEN}" "$QUERY_URL")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')
echo "---------"
echo "HTTP Status Code: $HTTP_CODE"
echo "$BODY"
echo "---------"


