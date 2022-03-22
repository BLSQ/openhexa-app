from hexa.plugins.connector_airflow.models import DAGRun


class DAGRunUser:
    """User model (not stored in DB) used to allow an Airflow DAG run to authenticate through a simple token
    (see middlewares.py in this module)
    """

    def __init__(self, dag_run: DAGRun):
        super().__init__()
        self.dag_run: DAGRun = dag_run

    is_active = True
    is_authenticated = True

    def get_username(self):
        return f"dag_{self.dag_run.id}"

    def natural_key(self):
        return self.dag_run.id
