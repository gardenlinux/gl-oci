import subprocess
import shlex

import os
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
ZOT_CONFIG_FILE = f"/zot/config.json"

def spawn_background_process(cmd):
    args = shlex.split(cmd)
    process = subprocess.Popen(
        args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    return process


def call_command(cmd):
    try:
        args = shlex.split(cmd)
        result = subprocess.run(
            args, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        output = result.stdout.decode("utf-8")
        return output

    except subprocess.CalledProcessError as e:
        error_message = e.stderr.decode("utf-8")
        return f"An error occurred: {error_message}"
