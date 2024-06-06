import oras.client


class OrasConnectionManager:
    def __init__(self, hostname, username, token):
        self.username = username
        self.token = token
        self.hostname = hostname
        self.client = None

    def connect(self):
        self.client = oras.client.OrasClient(hostname=self.hostname)
        self.client.set_token_auth(self.token)
        self.client.login(insecure=False, username=self.username, password=self.token)
        print(f"Logged in {self.hostname}")

    def disconnect(self):
        if self.client:
            self.client.logout(self.hostname)
            self.client = None
            print(f"Logged out {self.hostname}")