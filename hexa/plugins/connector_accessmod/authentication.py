import uuid


class DAGRunUser:
    def __init__(self, dag_run_id: uuid.UUID):
        super().__init__()
        self.dag_run_id = dag_run_id

    is_active = True
    is_authenticated = True

    def get_username(self):
        return f"dag_{self.dag_run_id}"

    def natural_key(self):
        return self.dag_run_id
