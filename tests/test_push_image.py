import subprocess
import io
from dotenv import load_dotenv
import pytest
from click.testing import CliRunner
from gloci.cli import cli

CONTAINER_NAME_ZOT_EXAMPLE = "127.0.0.1:18081/examplecontainer2"


@pytest.mark.usefixtures('zot_session')
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
        if result.exception:
            print(result.exception)
        try:
            print(f"Output: {result.stderr}")
        except ValueError:
            print("No stderr captured.")
    assert result.exit_code == 0
