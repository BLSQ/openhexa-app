from google.cloud._helpers import _bytes_to_unicode


class MockBlob:
    def __init__(
        self,
        name,
        bucket,
        chunk_size=None,
        encryption_key=None,
        kms_key_name=None,
        generation=None,
    ):
        self.name = _bytes_to_unicode(name)
        self.chunk_size = chunk_size  # Check that setter accepts value.
        self._bucket = bucket
        # self._acl = ObjectACL(self)
        if encryption_key is not None and kms_key_name is not None:
            raise ValueError(
                "Pass at most one of 'encryption_key' " "and 'kms_key_name'"
            )

        self._encryption_key = encryption_key

        if kms_key_name is not None:
            self._properties["kmsKeyName"] = kms_key_name

        if generation is not None:
            self._properties["generation"] = generation
