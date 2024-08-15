from .helper import call_command
import os
import tempfile
from .helper import spawn_background_process
import sys
import shutil
import json
import pytest

def write_zot_config(config_dict, file_path):
    with open(file_path, "w") as config_file:
        json.dump(config_dict, config_file, indent=4)

@pytest.fixture(autouse=False, scope="function")
def zot_session():
    print("start zot session")
    zot_config = {
        "distSpecVersion": "1.1.0",
        "storage": {"rootDirectory": "output/registry/zot"},
        "http": {"address": "127.0.0.1", "port": "18081"},
        "log": {"level": "warn"},
    }

    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp_config_file:
        write_zot_config(zot_config, temp_config_file.name)
        zot_config_file_path = temp_config_file.name

    print(f"Spawning zot registry with config {zot_config_file_path}")
    zot_process = spawn_background_process(
        f"zot serve {zot_config_file_path}",
        stdout=sys.stdout,
        stderr=sys.stderr,
    )

    yield zot_process
    print("clean up zot session")

    zot_process.terminate()

    if os.path.isdir("./output"):
        shutil.rmtree("./output")
    if os.path.isfile(zot_config_file_path):
        os.remove(zot_config_file_path)


def pytest_sessionstart(session):
    call_command("./cert/gencert.sh")


def pytest_sessionfinish(session):
    if os.path.isfile("./cert/oci-sign.crt"):
        os.remove("./cert/oci-sign.crt")
    if os.path.isfile("./cert/oci-sign.key"):
        os.remove("./cert/oci-sign.key")
