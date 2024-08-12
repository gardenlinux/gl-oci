import hashlib
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature
from cryptography import x509
import base64


def sign_data(data_str: str, private_key_file_path: str) -> str:
    with open(private_key_file_path, "rb") as key_file:
        private_key = load_pem_private_key(
            key_file.read(), password=None, backend=default_backend()
        )

    signature = private_key.sign(
        data_str.encode("utf-8"),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),  # Mask generation function based on SHA-256
            salt_length=padding.PSS.MAX_LENGTH,  # Maximum salt length
        ),
        hashes.SHA256(),
    )
    return base64.b64encode(signature).decode("utf-8")


def verify_signature(data_str: str, signature: str, public_key_file_path: str):
    with open(public_key_file_path, "rb") as cert_file:
        cert = x509.load_pem_x509_certificate(cert_file.read(), default_backend())
        public_key = cert.public_key()
    try:
        public_key.verify(
            base64.b64decode(signature),
            data_str.encode("utf-8"),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),  # Mask generation function based on SHA-256
                salt_length=padding.PSS.MAX_LENGTH,  # Maximum salt length
            ),
            hashes.SHA256(),
        )
    except InvalidSignature:
        raise ValueError(f"Invalid Signature {signature} for data: {data_str}")


def verify_sha256(checksum: str, data: bytes):
    data_checksum = f"sha256:{hashlib.sha256(data).hexdigest()}"
    if checksum != data_checksum:
        raise ValueError(f"Invalid checksum. {checksum} != {data_checksum}")


def calculate_sha256(file_path: str) -> str:
    """Calculate the SHA256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()
