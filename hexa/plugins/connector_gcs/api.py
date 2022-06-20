from __future__ import annotations

import binascii
import collections
import datetime
import hashlib

import six
from django.conf import settings
from google.cloud import storage
from google.cloud.iam_credentials_v1 import IAMCredentialsClient
from google.oauth2 import service_account
from google.protobuf import duration_pb2
from six.moves.urllib.parse import quote

import hexa.plugins.connector_gcs.models as models


class GCSApiError(Exception):
    pass


def _build_app_gcs_credentials(*, credentials: models.Credentials):
    json_cred = {
        "type": "service_account",
        "project_id": credentials.project_id,
        "private_key_id": credentials.private_key_id,
        "private_key": credentials.private_key,
        "client_email": credentials.client_email,
        "client_id": credentials.client_id,
        "auth_uri": credentials.auth_uri,
        "token_uri": credentials.token_uri,
        "auth_provider_x509_cert_url": credentials.auth_provider_x509_cert_url,
        "client_x509_cert_url": credentials.client_x509_cert_url,
    }
    return service_account.Credentials.from_service_account_info(json_cred)


def _build_app_short_lived_credentials(*, credentials: models.Credentials):
    token_lifetime = 3600
    if settings.GCS_TOKEN_LIFETIME is not None:
        token_lifetime = int(settings.GCS_TOKEN_LIFETIME)
    gcs_credentials = _build_app_gcs_credentials(credentials=credentials)
    iam_credentials = IAMCredentialsClient(credentials=gcs_credentials)
    token = iam_credentials.generate_access_token(
        name=f"projects/-/serviceAccounts/{gcs_credentials._service_account_email}",
        scope=["https://www.googleapis.com/auth/devstorage.full_control"],
        lifetime=duration_pb2.Duration(seconds=token_lifetime),
    )
    return token


def generate_signed_url(
    google_credentials,
    bucket_name,
    object_name,
    subresource=None,
    expiration=604800,
    http_method="GET",
    query_parameters=None,
    headers=None,
):

    if expiration > 604800:
        raise GCSApiError(
            "Expiration Time can't be longer than 604800 seconds (7 days)."
        )

    escaped_object_name = quote(six.ensure_binary(object_name), safe=b"/~")
    canonical_uri = "/{}".format(escaped_object_name)

    datetime_now = datetime.datetime.now(tz=datetime.timezone.utc)
    request_timestamp = datetime_now.strftime("%Y%m%dT%H%M%SZ")
    datestamp = datetime_now.strftime("%Y%m%d")

    client_email = google_credentials.service_account_email
    credential_scope = "{}/auto/storage/goog4_request".format(datestamp)
    credential = "{}/{}".format(client_email, credential_scope)

    if headers is None:
        headers = dict()
    host = "{}.storage.googleapis.com".format(bucket_name)
    headers["host"] = host

    canonical_headers = ""
    ordered_headers = collections.OrderedDict(sorted(headers.items()))
    for k, v in ordered_headers.items():
        lower_k = str(k).lower()
        strip_v = str(v).lower()
        canonical_headers += "{}:{}\n".format(lower_k, strip_v)

    signed_headers = ""
    for k, _ in ordered_headers.items():
        lower_k = str(k).lower()
        signed_headers += "{};".format(lower_k)
    signed_headers = signed_headers[:-1]  # remove trailing ';'

    if query_parameters is None:
        query_parameters = dict()
    query_parameters["X-Goog-Algorithm"] = "GOOG4-RSA-SHA256"
    query_parameters["X-Goog-Credential"] = credential
    query_parameters["X-Goog-Date"] = request_timestamp
    query_parameters["X-Goog-Expires"] = expiration
    query_parameters["X-Goog-SignedHeaders"] = signed_headers
    if subresource:
        query_parameters[subresource] = ""

    canonical_query_string = ""
    ordered_query_parameters = collections.OrderedDict(sorted(query_parameters.items()))
    for k, v in ordered_query_parameters.items():
        encoded_k = quote(str(k), safe="")
        encoded_v = quote(str(v), safe="")
        canonical_query_string += "{}={}&".format(encoded_k, encoded_v)
    canonical_query_string = canonical_query_string[:-1]  # remove trailing '&'

    canonical_request = "\n".join(
        [
            http_method,
            canonical_uri,
            canonical_query_string,
            canonical_headers,
            signed_headers,
            "UNSIGNED-PAYLOAD",
        ]
    )

    canonical_request_hash = hashlib.sha256(canonical_request.encode()).hexdigest()

    string_to_sign = "\n".join(
        [
            "GOOG4-RSA-SHA256",
            request_timestamp,
            credential_scope,
            canonical_request_hash,
        ]
    )

    # signer.sign() signs using RSA-SHA256 with PKCS1v15 padding
    signature = binascii.hexlify(
        google_credentials.signer.sign(string_to_sign)
    ).decode()

    scheme_and_host = "{}://{}".format("https", host)
    signed_url = "{}{}?{}&x-goog-signature={}".format(
        scheme_and_host, canonical_uri, canonical_query_string, signature
    )

    return signed_url


def generate_download_url(
    *, principal_credentials: models.Credentials, bucket: models.Bucket, target_key: str
):
    google_credentials = _build_app_gcs_credentials(credentials=principal_credentials)
    return generate_signed_url(
        google_credentials=google_credentials,
        bucket_name=bucket.name,
        object_name=target_key,
        expiration=3600,
    )


def _is_dir(blob):
    return blob.size == 0 and blob.name.endswith("/")


def list_objects_metadata(*, credentials: models.Credentials, bucket: models.Bucket):

    gcs_credentials = _build_app_gcs_credentials(credentials=credentials)
    client = storage.Client(credentials=gcs_credentials)
    gcs_bucket = client.get_bucket(bucket.name)
    objects = []

    blobs = list(client.list_blobs(gcs_bucket))
    for blob in blobs:
        objects.append(
            {
                "name": blob.name,
                "size": blob.size,
                "updated": blob.updated,
                "etag": blob.etag,
                "type": "directory" if _is_dir(blob) else "file",
            }
        )

    return objects
