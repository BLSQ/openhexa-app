def list_objects(bucket, fs, path):
    for object_data in fs.ls(path, detail=True):
        if object_data["Key"] == f"{path}/" and object_data["type"] != "directory":
            # Detects the current directory. Ignore it as we already got it from the parent listing
            continue

        # Manually add a / at the end of the directory paths to be more POSIX-compliant
        if object_data["type"] == "directory" and not object_data["Key"].endswith("/"):
            object_data["Key"] = object_data["Key"] + "/"

        # ETag seems to sometimes contain quotes, probably because of a bug in s3fs
        if "ETag" in object_data and object_data["ETag"].startswith('"'):
            object_data["ETag"] = object_data["ETag"].replace('"', "")

        yield object_data

        if object_data["type"] == "directory":
            yield from list_objects(bucket, fs, object_data["Key"])


def sync_directories(bucket, fs, s3_objects):
    created_count = 0
    updated_count = 0
    identical_count = 0
    new_orphans_count = 0

    existing_directories_by_uid = {
        str(x.id): x for x in bucket.object_set.filter(s3_type="directory")
    }

    for s3_obj in s3_objects:
        if s3_obj["type"] == "directory":
            metadata_path = os.path.join(s3_obj["Key"], METADATA_FILENAME)
            s3_uid = None
            if fs.exists(metadata_path):
                with fs.open(metadata_path, mode="rb") as fd:
                    try:
                        metadata = json.load(fd)
                        s3_uid = metadata.get("uid")
                    except json.decoder.JSONDecodeError:
                        pass

            db_obj = existing_directories_by_uid.get(s3_uid)
            if db_obj:
                if db_obj.s3_key != s3_obj["Key"]:  # Directory moved
                    db_obj.update_metadata(s3_obj)
                    db_obj.save()
                    updated_count += 1
                else:  # Not moved
                    identical_count += 1
                del existing_directories_by_uid[s3_uid]
            else:  # Not in the DB yet
                db_obj = Object.create_from_object_data(bucket, s3_obj)
                metadata_path = os.path.join(db_obj.s3_key, METADATA_FILENAME)
                with fs.open(metadata_path, mode="wb") as fd:
                    fd.write(json.dumps({"uid": str(db_obj.id)}).encode())
                created_count += 1

    for obj in existing_directories_by_uid.values():
        if not obj.orphan:
            new_orphans_count += 1
            obj.orphan = True
            obj.save()

    return DatasourceSyncResult(
        datasource=bucket,
        created=created_count,
        updated=updated_count,
        identical=identical_count,
        orphaned=new_orphans_count,
    )


def sync_objects(bucket, fs, discovered_objects):
    existing_objects = list(bucket.object_set.filter(s3_type="file"))
    existing_by_key = {x.s3_key: x for x in existing_objects}

    created = {}
    updated_count = 0
    identical_count = 0
    merged_count = 0

    for object_data in discovered_objects:
        if object_data["type"] != "file":
            continue
        key = object_data["Key"]
        if key.endswith("/.openhexa.json"):
            continue

        if key in existing_by_key:
            if object_data.get("ETag") == existing_by_key[key].s3_etag:
                identical_count += 1
            else:
                existing_by_key[key].update_metadata(object_data)
                existing_by_key[key].save()
                updated_count += 1
            del existing_by_key[key]
        else:
            created[key] = Object.create_from_object_data(bucket, object_data)

    orphans_by_etag = {x.s3_etag: x for x in existing_by_key.values()}

    for created_obj in created.values():
        etag = created_obj.s3_etag
        orphan_obj = orphans_by_etag.get(etag)
        if orphan_obj:
            del orphans_by_etag[etag]
            orphan_obj.delete()
            merged_count += 1

    new_orphans_count = len([x for x in orphans_by_etag.values() if not x.orphan])

    for obj in orphans_by_etag.values():
        obj.orphan = True
        obj.save()

    return DatasourceSyncResult(
        datasource=bucket,
        created=len(created) - merged_count,
        updated=updated_count + merged_count,
        identical=identical_count,
        orphaned=new_orphans_count,
    )
