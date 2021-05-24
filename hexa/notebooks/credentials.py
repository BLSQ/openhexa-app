class NotebooksCredentials:
    """This class acts as a container for credentials to be provided to the notebooks component."""

    def __init__(self, user):
        self.user = user
        self.data = {}

    @property
    def authenticated(self):
        return self.user.is_authenticated

    def update_data(self, env_dict):
        self.data.update(**env_dict)

    def to_dict(self):
        return {"username": self.user.username, "data": self.data}
