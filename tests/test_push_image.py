import pytest
from click.testing import CliRunner
from gloci.cli import cli
from gloci.commands.image import setup_registry

CONTAINER_NAME_ZOT_EXAMPLE = "127.0.0.1:18081/examplecontainer2"


@pytest.mark.usefixtures("zot_session")
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

    container_name = f"{CONTAINER_NAME_ZOT_EXAMPLE}:{version}"
    registry = setup_registry(
        container_name,
        insecure=True,
        private_key="cert/oci-sign.key",
        public_key="cert/oci-sign.crt",
    )
    registry.push_image_manifest(arch, cname, version, info_yaml_path)


@pytest.mark.usefixtures("zot_session")
@pytest.mark.parametrize(
    "info_yaml_path, version, cname, arch",
    [
        ("example-data/info_1.yaml", "today", "yolo-example_dev", "arm64"),
        ("example-data/info_1.yaml", "today", "yolo-example_dev", "amd64"),
        ("example-data/info_2.yaml", "today", "yolo-example_dev", "arm64"),
        ("example-data/info_2.yaml", "today", "yolo-example_dev", "amd64"),
    ],
)
def test_push_example_cli(info_yaml_path, version, cname, arch):
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
        catch_exceptions=False,
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
