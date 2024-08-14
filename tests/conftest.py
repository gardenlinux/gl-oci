from .helper import call_command
import os


def pytest_sessionstart(session):
    call_command("./cert/gencert.sh")


def pytest_sessionfinish(session):
    if os.path.isfile("./cert/oci-sign.crt"):
        os.remove("./cert/oci-sign.crt")
    if os.path.isfile("./cert/oci-sign.key"):
        os.remove("./cert/oci-sign.key")