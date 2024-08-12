from gloci.oras.crypto import sign_data, verify_signature
import string
import random


def generate_random_string(length: int):
    characters = string.ascii_letters + string.digits + string.punctuation
    return "".join(random.choice(characters) for _ in range(length))


def test_signing():
    data = generate_random_string(100)
    public_key_path = "cert/oci-sign.crt"
    private_key_path = "cert/oci-sign.key"

    signature = sign_data(data, private_key_path)

    verify_signature(data, signature, public_key_path)
