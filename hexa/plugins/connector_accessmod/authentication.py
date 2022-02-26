import uuid


class DAGRunUser:
    """User model (not stored in DB) used to allow an Airflow DAG run to authenticate through a simple token
    (see middlewares.py in this module)
    """

    def __init__(self, dag_run_id: uuid.UUID):
        super().__init__()
        self.dag_run_id = dag_run_id

    is_active = True
    is_authenticated = True

    def get_username(self):
        return f"dag_{self.dag_run_id}"

    def natural_key(self):
        return self.dag_run_id
