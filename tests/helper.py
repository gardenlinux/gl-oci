import subprocess
import shlex

def spawn_background_process(command):
    process = subprocess.Popen(command)
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
