import base64
import contextvars
from tornado import web
from s3contents.genericmanager import GenericContentsManager

# Used as a "registry" for uploads.
# TODO: periodic cleanup - but when ? As is, could cause memory issues
content_chunks = contextvars.ContextVar("jupyterlab_content_chunks", default={})


def store_content_chunk(path: str, content: str):
    """Store a base64 chunk in the registry as bytes"""

    current_value = content_chunks.get()

    if path not in current_value:
        current_value[path] = []

    current_value[path].append(base64.b64decode(content.encode("ascii"), validate=True))


def assemble_chunks(path: str) -> str:
    """Assemble the chunk bytes into a single base64 string"""

    current_value = content_chunks.get()

    if path not in current_value:
        raise ValueError(f"No chunk for path {path}")

    return base64.b64encode(b"".join(current_value[path])).decode("ascii")


def delete_chunks(path):
    """Should be called once the upload is complete to free the memory"""

    current_value = content_chunks.get()
    del current_value[path]


def save(manager_class, manager: GenericContentsManager, model, path=""):
    """This function is used to "override" GenericContentsManager.save() in our custom manager for S3 and GCS.
    Code inspired from notebook.services.contents.largefilemanager.
    Todo: PR in s3contents?
    """

    chunk = model.get("chunk", None)
    if chunk is not None:
        if "type" not in model:
            raise web.HTTPError(400, "No file type provided")
        if model["type"] != "file":
            raise web.HTTPError(
                400,
                'File type "{}" is not supported for large file transfer'.format(
                    model["type"]
                ),
            )
        if "content" not in model and model["type"] != "directory":
            raise web.HTTPError(400, "No file content provided")

        try:
            if chunk == 1:
                manager.log.debug(
                    "S3contents.GenericManager.save %s: '%s'", model, path
                )
                manager.run_pre_save_hook(model=model, path=path)
            # Store the chunk in our registry
            store_content_chunk(path, model["content"])
        except Exception as e:
            manager.log.error("Error while saving file: %s %s", path, e, exc_info=True)
            raise web.HTTPError(
                500, "Unexpected error while saving file: %s %s" % (path, e)
            )

        if chunk == -1:
            # Last chunk: we want to combine the chunks in the registry to compose the full file content
            model["content"] = assemble_chunks(path)
            delete_chunks(path)
            manager._save_file(model, path)

        return manager.get(path, content=False)
    else:
        return super(manager_class, manager).save(model, path)
