import json
import logging

import boto3
import psycopg2
from botocore.config import Config as BotoConfig
from google.cloud import storage as gcs_storage
from openhexa.toolbox.dhis2 import DHIS2
from openhexa.toolbox.iaso import IASO

from .models import ConnectionType

logger = logging.getLogger(__name__)

CONNECT_TIMEOUT = 10


def test_connection(connection_type: str, fields: dict[str, str]) -> tuple[bool, str | None]:
    testers = {
        ConnectionType.DHIS2: _test_dhis2,
        ConnectionType.IASO: _test_iaso,
        ConnectionType.POSTGRESQL: _test_postgresql,
        ConnectionType.S3: _test_s3,
        ConnectionType.GCS: _test_gcs,
    }
    tester = testers.get(connection_type)
    if not tester:
        return False, f"Testing is not supported for {connection_type} connections"

    try:
        return tester(fields)
    except Exception as e:
        logger.exception("Connection test failed for %s", connection_type)
        return False, str(e)


def _test_dhis2(fields: dict) -> tuple[bool, str | None]:
    client = DHIS2(
        url=fields["url"],
        username=fields["username"],
        password=fields["password"],
    )
    if not client.ping():
        return False, "DHIS2 instance is not reachable"
    client.me()
    return True, None


def _test_iaso(fields: dict) -> tuple[bool, str | None]:
    client = IASO(
        url=fields["url"],
        username=fields["username"],
        password=fields["password"],
    )
    response = client.api_client.get("api/profiles/me/")
    client.api_client.raise_if_error(response)
    return True, None


def _test_postgresql(fields: dict) -> tuple[bool, str | None]:
    conn = psycopg2.connect(
        host=fields["host"],
        port=int(fields.get("port", 5432)),
        user=fields["username"],
        password=fields["password"],
        dbname=fields["db_name"],
        connect_timeout=CONNECT_TIMEOUT,
    )
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
    finally:
        conn.close()
    return True, None


def _test_s3(fields: dict) -> tuple[bool, str | None]:
    client = boto3.client(
        "s3",
        aws_access_key_id=fields.get("access_key_id") or None,
        aws_secret_access_key=fields.get("access_key_secret") or None,
        config=BotoConfig(
            connect_timeout=CONNECT_TIMEOUT,
            read_timeout=CONNECT_TIMEOUT,
            retries={"total_max_attempts": 1},
        ),
    )
    client.head_bucket(Bucket=fields["bucket_name"])
    return True, None


def _test_gcs(fields: dict) -> tuple[bool, str | None]:
    creds = json.loads(fields["service_account_key"])
    client = gcs_storage.Client.from_service_account_info(creds)
    bucket = client.bucket(fields["bucket_name"])
    list(bucket.list_blobs(max_results=1, timeout=CONNECT_TIMEOUT))
    return True, None
