class NotebooksCredentials:
    """This class acts as a container for credentials to be provided to the notebooks component."""

    def __init__(self, user):
        self.user = user
        self.env = {}

    @property
    def authenticated(self):
        return self.user.is_authenticated and self.user.is_superuser

    def update_env(self, env_dict):
        self.env.update(**env_dict)

    def to_dict(self):
        return {"username": self.user.username, "env": self.env}
