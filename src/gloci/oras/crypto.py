import hashlib
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature
from cryptography import x509


def sign_data(data_str: str, private_key_file_path: str):

    with open(private_key_file_path, "rb") as key_file:
        private_key = load_pem_private_key(
            key_file.read(), password=None, backend=default_backend()
        )

    signature = private_key.sign(
        data_str.encode("utf-8"),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256(),
    )

    return signature.hex()


def verify_signature(data_str: str, signature: str, public_key_file_path: str):
    if public_key_file_path is None:
        return False
    with open(public_key_file_path, "rb") as cert_file:
        cert = x509.load_pem_x509_certificate(cert_file.read(), default_backend())
        public_key = cert.public_key()

    try:
        public_key.verify(
            signature.encode("utf-8"),
            data_str.encode("utf-8"),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256(),
        )
        return True
    except InvalidSignature:
        return False


def verify_sha256(checksum: str, data):
    data_checksum = f"sha256:{hashlib.sha256(data).hexdigest()}"
    if checksum != data_checksum:
        raise ValueError(f"Invalid checksum. {checksum} != {data_checksum}")


def calculate_sha256(file_path):
    """Calculate the SHA256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            # Read the file in chunks of 4KB
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        # Return the hexadecimal digest of the checksum
        return sha256_hash.hexdigest()
    except FileNotFoundError:
        print(f"File {file_path} not found.")
        return None
