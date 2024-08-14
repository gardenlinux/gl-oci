import subprocess
from dotenv import load_dotenv
import pytest
import time
from click.testing import CliRunner
from gloci.cli import cli
from .helper import spawn_background_process
import os

CONTAINER_NAME_ZOT_EXAMPLE = "localhost:8081/examplecontainer2"
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
ZOT_CONFIG_FILE = f"{ROOT_DIR}/../zot/config.json"


@pytest.fixture(autouse=True)
def setup_test_environment():
    print("Spawning zot registry")
    zot_process = spawn_background_process(f"zot serve {ZOT_CONFIG_FILE}")
    time.sleep(3)

    yield zot_process


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
