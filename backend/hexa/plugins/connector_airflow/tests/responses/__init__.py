dags = {
    "dags": [
        {
            "dag_id": "hello_world",
            "description": "Hello world example",
            "file_token": "Ii9vcHQvYWlyZmxvdy9kYWdzL3JlcG8vZGFncy9oZWxsb3dvcmxkLnB5Ig.x6F3mxeBdDLzg9-dB34gk-iOU2o",
            "fileloc": "/opt/airflow/dags/repo/dags/helloworld.py",
            "is_active": True,
            "is_paused": False,
            "is_subdag": False,
            "owners": ["airflow"],
            "root_dag_id": None,
            "schedule_interval": {
                "__type": "CronExpression",
                "value": "* * * * *",
            },
            "tags": [],
        },
        {
            "dag_id": "same_old",
            "description": "Same old example",
            "file_token": "Ii9vcHQvYWlyZmxvdy9kYWdzL3JlcG8vZGFncy9oZWxsb3dvcmxkLnB5Ig.x6F3mxeBdDLzg9-dB34gk-iOU2o",
            "fileloc": "/opt/airflow/dags/repo/dags/sameold.py",
            "is_active": True,
            "is_paused": True,
            "is_subdag": False,
            "owners": ["airflow"],
            "root_dag_id": None,
            "schedule_interval": {
                "__type": "CronExpression",
                "value": "* * * * *",
            },
            "tags": [],
        },
    ],
    "total_entries": 2,
}


dag_run_hello_world_1 = {
    "conf": {},
    "dag_id": "hello_world",
    "dag_run_id": "hello_world_run_1",
    "end_date": "2021-10-08T16:42:16.189200+00:00",
    "execution_date": "2021-10-08T16:41:00+00:00",
    "external_trigger": False,
    "start_date": "2021-10-08T16:42:00.830209+00:00",
    "state": "success",
}
dag_run_hello_world_2 = {
    "conf": {},
    "dag_id": "hello_world",
    "dag_run_id": "hello_world_run_2",
    "end_date": "2021-10-08T16:43:16.629694+00:00",
    "execution_date": "2021-10-08T16:42:00+00:00",
    "external_trigger": False,
    "start_date": "2021-10-08T16:43:01.101863+00:00",
    "state": "success",
}
dag_runs_hello_world = {
    "dag_runs": [
        dag_run_hello_world_1,
        dag_run_hello_world_2,
    ],
    "total_entries": 2,
}

dag_run_same_old_1 = {
    "conf": {},
    "dag_id": "same_old",
    "dag_run_id": "same_old_run_1",
    "end_date": "2021-10-08T16:42:16.189200+00:00",
    "execution_date": "2021-10-08T16:41:00+00:00",
    "external_trigger": False,
    "start_date": "2021-10-08T16:42:00.830209+00:00",
    "state": "success",
}

dag_run_same_old_2 = {
    "conf": {},
    "dag_id": "same_old",
    "dag_run_id": "same_old_run_2",
    "end_date": "2021-10-09T16:42:16.189200+00:00",
    "execution_date": "2021-10-09T16:41:00+00:00",
    "external_trigger": False,
    "start_date": "2021-10-09T16:42:00.830209+00:00",
    "state": "queued",
}
dag_runs_same_old = {
    "dag_runs": [
        dag_run_same_old_1,
        dag_run_same_old_2,
    ],
    "total_entries": 2,
}

dag_continuous_sync1 = {
    "dag_runs": [
        {
            "conf": {},
            "dag_id": "hello_world",
            "dag_run_id": "run1",
            "end_date": "2022-02-05T13:42:42.140724+00:00",
            "execution_date": "2022-02-05T13:42:25.261989+00:00",
            "external_trigger": True,
            "start_date": "2022-02-05T13:42:25.615264+00:00",
            "state": "success",
        },
        {
            "conf": {},
            "dag_id": "hello_world",
            "dag_run_id": "untracked",
            "end_date": "2022-02-05T13:40:44.185503+00:00",
            "execution_date": "2022-02-05T13:39:50.613372+00:00",
            "external_trigger": True,
            "start_date": "2022-02-05T13:39:52.082496+00:00",
            "state": "success",
        },
    ],
    "total_entries": 2,
}

dag_continuous_sync2 = {
    "dag_runs": [
        {
            "conf": {},
            "dag_id": "hello_world",
            "dag_run_id": "run1",
            "end_date": "2022-02-05T13:42:42.140724+00:00",
            "execution_date": "2022-02-05T13:42:25.261989+00:00",
            "external_trigger": True,
            "start_date": "2022-02-05T13:42:25.615264+00:00",
            "state": "success",
        },
        {
            "conf": {},
            "dag_id": "hello_world",
            "dag_run_id": "run2",
            "end_date": "2022-02-05T13:40:44.185503+00:00",
            "execution_date": "2022-02-05T13:39:50.613372+00:00",
            "external_trigger": True,
            "start_date": "2022-02-05T13:39:52.082496+00:00",
            "state": "success",
        },
    ],
    "total_entries": 2,
}
