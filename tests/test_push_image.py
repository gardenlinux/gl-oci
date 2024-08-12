import subprocess
from dotenv import load_dotenv
import shlex
import pytest
from click.testing import CliRunner
from gloci.cli import cli



ZOT_CONFIG_FILE = "./zot/config.json"
CONTAINER_NAME_ZOT_EXAMPLE = "localhost:8081/examplecontainer2"

def spawn_background_process(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return process

def call_command(cmd):
    try:
        args = shlex.split(cmd)
        result = subprocess.run(args, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        return output
    
    except subprocess.CalledProcessError as e:
        error_message = e.stderr.decode('utf-8')
        return f"An error occurred: {error_message}"


@pytest.fixture
def setup_test_environment():
    zot_process = spawn_background_process(f"zot serve {ZOT_CONFIG_FILE}")

    yield zot_process

    zot_process.terminate()
    try:
        zot_process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        zot_process.kill()
        zot_process.wait()


@pytest.mark.parametrize("info_yaml_path, version, cname, arch", [
    ("example-data/info_1.yaml", "today", "yolo-example_dev", "arm64"),
    ("example-data/info_1.yaml", "today", "yolo-example_dev", "amd64"),
    ("example-data/info_2.yaml", "today", "yolo-example_dev", "arm64"),
    ("example-data/info_2.yaml", "today", "yolo-example_dev", "amd64"),

])
def test_push_example(info_yaml_path, version, cname, arch):
    load_dotenv()
    runner = CliRunner()
    result = runner.invoke(cli, [
        'image', 'push',
        '--container', CONTAINER_NAME_ZOT_EXAMPLE,
        '--version', version,
        '--architecture', arch,
        '--cname', cname,
        '--info_yaml', info_yaml_path
    ])
    if result.exit_code != 0:
        # Print the output and error message for debugging
        print(f"Exit Code: {result.exit_code}")
        print(f"Output: {result.output}")
        print(f"Error: {result.stderr}")  # If stderr was captured (can also be in result.output)

    assert result.exit_code == 0






    
