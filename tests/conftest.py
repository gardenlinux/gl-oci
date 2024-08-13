from .helper import call_command

def pytest_sessionstart(session):
    call_command("./cert/gencert.sh")

