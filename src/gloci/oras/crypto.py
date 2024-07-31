import hashlib


def calculate_sha1(file_path):
    """Calculate the SHA1 checksum of a file."""
    sha1_hash = hashlib.sha1()
    try:
        with open(file_path, "rb") as f:
            # Read the file in chunks of 4KB
            for byte_block in iter(lambda: f.read(4096), b""):
                sha1_hash.update(byte_block)
        # Return the hexadecimal digest of the checksum
        return sha1_hash.hexdigest()
    except FileNotFoundError:
        print(f"File {file_path} not found.")
        return None


def calculate_md5(file_path):
    """Calculate the MD5 checksum of a file."""
    md5_hash = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            # Read the file in chunks of 4KB
            for byte_block in iter(lambda: f.read(4096), b""):
                md5_hash.update(byte_block)
        # Return the hexadecimal digest of the checksum
        return md5_hash.hexdigest()
    except FileNotFoundError:
        print(f"File {file_path} not found.")
        return None


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
