from dotenv import load_dotenv
import pytest
import tempfile
from click.testing import CliRunner
from gloci.cli import cli
from .helper import spawn_background_process
import os
import shutil
import json

CONTAINER_NAME_ZOT_EXAMPLE = "localhost:18081/examplecontainer2"

def write_zot_config(config_dict, file_path):
    with open(file_path, 'w') as config_file:
        json.dump(config_dict, config_file, indent=4)


@pytest.fixture(autouse=True)
def setup_test_environment():
    zot_config = {
        "distSpecVersion": "1.1.0",
        "storage": {
            "rootDirectory": "output/registry/zot"
        },
        "http": {
            "address": "127.0.0.1",
            "port": "18081"
        },
        "log": {
            "level": "warn"
        }
    }

    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp_config_file:
        write_zot_config(zot_config, temp_config_file.name)
        zot_config_file_path = temp_config_file.name
    print(f"Spawning zot registry with config {zot_config_file_path}")
    zot_process = spawn_background_process(f"zot serve {zot_config_file_path}")

    yield zot_process

    if os.path.isdir("./output"):
        shutil.rmtree("./output")
    if os.path.isfile(zot_config_file_path):
        os.remove(zot_config_file_path)

@pytest.mark.parametrize(
    "info_yaml_path, version, cname, arch",
    [
        ("example-data/info_1.yaml", "today", "yolo-example_dev", "arm64"),
        ("example-data/info_1.yaml", "today", "yolo-example_dev", "amd64"),
        ("example-data/info_2.yaml", "today", "yolo-example_dev", "arm64"),
        ("example-data/info_2.yaml", "today", "yolo-example_dev", "amd64"),
    ],
)
def test_push_example(info_yaml_path, version, cname, arch):
    load_dotenv()
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "image",
            "push",
            "--container",
            CONTAINER_NAME_ZOT_EXAMPLE,
            "--version",
            version,
            "--architecture",
            arch,
            "--cname",
            cname,
            "--info_yaml",
            info_yaml_path,
        ],
    )
    if result.exit_code != 0:
        print(f"Exit Code: {result.exit_code}")
        print(f"Output: {result.output}")
    assert result.exit_code == 0
