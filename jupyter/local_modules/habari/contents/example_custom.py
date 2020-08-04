import typing

from notebook.services.contents.checkpoints import GenericCheckpointsMixin, Checkpoints
from notebook.utils import is_file_hidden, is_hidden
from tornado import web
from notebook.services.contents.manager import ContentsManager
import gcsfs
from traitlets import Unicode
import dateutil.parser
import mimetypes
from base64 import encodebytes, decodebytes
import nbformat


class NoOpCheckpoints(GenericCheckpointsMixin, Checkpoints):
    """requires the following methods:"""

    def create_file_checkpoint(self, content, format, path):
        return {
            "id": "checkpoint",
            "last_modified": dateutil.parser.parse("2020-05-29T10:00:00Z"),
        }

    def create_notebook_checkpoint(self, nb, path):
        return {
            "id": "checkpoint",
            "last_modified": dateutil.parser.parse("2020-05-29T10:00:00Z"),
        }

    def get_file_checkpoint(self, checkpoint_id, path):
        """ -> {'type': 'file', 'content': <str>, 'format': {'text', 'base64'}}"""

    def get_notebook_checkpoint(self, checkpoint_id, path):
        """ -> {'type': 'notebook', 'content': <output of nbformat.read>}"""

    def delete_checkpoint(self, checkpoint_id, path):
        """deletes a checkpoint for a file"""

    def list_checkpoints(self, path):
        """returns a list of checkpoint models for a given file,
        default just does one per file
        """
        return []

    def rename_checkpoint(self, checkpoint_id, old_path, new_path):
        """renames checkpoint from old path to new path"""


class HabariGCSFileSystem(gcsfs.GCSFileSystem):
    def __init__(self):
        super().__init__(
            cache_timeout=1
        )  # issue with cache_timeout=0 - see fsspec CacheDir

    def mkdir(self, path, **kwargs):
        if len(path) > 1 and "/" in path:
            with self.open(path, "wb") as f:
                f.path += "/"
                f.key += "/"

        super().mkdir(path, **kwargs)

    def ls(self, path, detail=False, **kwargs):
        objects = super().ls(path, detail, **kwargs)

        return [o for o in objects if o["name"].rstrip("/") != path]


class GCSManager(ContentsManager):
    bucket = Unicode(config=True)
    checkpoints_class = NoOpCheckpoints

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._fs = HabariGCSFileSystem()

    def get(
        self,
        path,
        content: bool = True,
        type: typing.Literal["file", "notebook", "directory"] = None,
        format: typing.Literal["text", "base64"] = None,
    ):
        path = path.strip("/")

        if not self.exists(path):
            raise web.HTTPError(404, "No such file or directory: %s" % path)

        if self.dir_exists(path):
            if type not in (None, "directory"):
                raise web.HTTPError(
                    400, "%s is a directory, not a %s" % (path, type), reason="bad type"
                )
            model = self._dir_model(path, content=content)
        elif type == "notebook" or (type is None and path.endswith(".ipynb")):
            model = self._notebook_model(path, content=content)
        else:
            if type == "directory":
                raise web.HTTPError(
                    400, "%s is not a directory" % path, reason="bad type"
                )
            model = self._file_model(path, content=content, format=format)
        return model

    def save(self, model, path=""):
        path = path.strip("/")

        if "type" not in model:
            raise web.HTTPError(400, "No file type provided")
        if "content" not in model and model["type"] != "directory":
            raise web.HTTPError(400, "No file content provided")

        gcs_path = self._get_gcs_path(path)
        self.log.debug("Saving %s", gcs_path)

        self.run_pre_save_hook(model=model, path=path)

        try:
            if model["type"] == "notebook":  # TODO: implement
                nb = nbformat.from_dict(model["content"])
                self.check_and_sign(nb, path)
                self._save_notebook(os_path, nb)
                # One checkpoint should always exist for notebooks.
                if not self.checkpoints.list_checkpoints(path):
                    self.create_checkpoint(path)
            elif model["type"] == "file":
                # Missing format will be handled internally by _save_file.
                self._save_file(gcs_path, model["content"], model.get("format"))
            elif model["type"] == "directory":
                self._save_directory(gcs_path)
            else:
                raise web.HTTPError(400, "Unhandled contents type: %s" % model["type"])
        except web.HTTPError:
            raise
        except Exception as e:
            self.log.error("Error while saving file: %s %s", path, e, exc_info=True)
            raise web.HTTPError(
                500, "Unexpected error while saving file: %s %s" % (path, e)
            )

        validation_message = None
        if model["type"] == "notebook":
            self.validate_notebook_model(model)
            validation_message = model.get("message", None)

        model = self.get(path, content=False)
        if validation_message:
            model["message"] = validation_message

        # self.run_post_save_hook(model=model, os_path=os_path)

        return model

    def file_exists(self, path: str = "") -> bool:
        path = path.strip("/")
        gcs_path = self._get_gcs_path(path)

        return self._fs.isfile(gcs_path)

    def dir_exists(self, path: str) -> bool:
        path = path.strip("/")

        gcs_path = self._get_gcs_path(path)

        return self._fs.isdir(gcs_path)

    def _get_gcs_path(self, path: str) -> str:
        return f"{self.bucket}/{path}".strip("/")

    def _base_model(self, path: str):
        gcs_path = self._get_gcs_path(path)
        info = self._fs.info(gcs_path)

        try:
            size = info["size"]
        except KeyError:
            self.log.warning("Unable to get size.")
            size = None

        try:
            last_modified = dateutil.parser.isoparse(info["updated"])
        except (KeyError, ValueError):
            self.log.warning("Invalid mtime %s for %s", info.get("updated"), gcs_path)
            last_modified = dateutil.parser.isoparse("2020-05-29T10:00:00Z")

        try:
            created = dateutil.parser.isoparse(info["timeCreated"])
        except (KeyError, ValueError):  # See above
            self.log.warning(
                "Invalid ctime %s for %s", info.get("timeCreated"), gcs_path
            )
            created = dateutil.parser.isoparse("2020-05-29T10:00:00Z")

        # Create the base model.
        model = {}
        model["name"] = path.rsplit("/", 1)[-1]  # basename?
        model["path"] = path.strip("/")  # gcs_path?
        model["last_modified"] = last_modified
        model["created"] = created
        model["content"] = None
        model["format"] = None
        model["mimetype"] = None
        model["size"] = size
        model["writable"] = True  # TODO: more fine-grained control?

        return model

    def _dir_model(self, path, content=True):
        """Build a model for a directory

        if content is requested, will include a listing of the directory
        """

        model = self._base_model(path)

        gcs_path = self._get_gcs_path(path)

        model["type"] = "directory"
        model["size"] = None
        if content:
            model["content"] = contents = []
            for child in self._fs.listdir(gcs_path):
                child_gcs_path = child["name"]
                child_api_path = child["name"].split("/", 1)[1]
                child_name = child_api_path.split("/")[-1]
                if self.should_list(child_name):
                    if self.allow_hidden or not is_file_hidden(child_gcs_path):
                        contents.append(self.get(child_api_path, content=False))

            model["format"] = "json"

        return model

    def should_list(self, name):
        if (
            name == ""
        ):  # empty files returned by GCS / directory markers? (try gsutil ls gs://bucket/dir/)
            return False

        return super().should_list(name)

    def _to_api_path(self, gcs_path: str):
        return gcs_path

    def _file_model(self, path, content=True, format=None):
        """Build a model for a file

        if content is requested, include the file contents.

        format:
          If 'text', the contents will be decoded as UTF-8.
          If 'base64', the raw bytes contents will be encoded as base64.
          If not specified, try to decode as UTF-8, and fall back to base64
        """
        model = self._base_model(path)
        model["type"] = "file"

        gcs_path = self._get_gcs_path(path)
        model["mimetype"] = mimetypes.guess_type(gcs_path)[0]

        if content:
            content, format = self._read_file(gcs_path, format)
            if model["mimetype"] is None:
                default_mime = {
                    "text": "text/plain",
                    "base64": "application/octet-stream",
                }[format]
                model["mimetype"] = default_mime

            model.update(
                content=content, format=format,
            )

        return model

    def _notebook_model(self, path, content=True):
        """Build a notebook model

        if content is requested, the notebook content will be populated
        as a JSON structure (not double-serialized)
        """
        model = self._base_model(path)
        model["type"] = "notebook"
        os_path = self._get_os_path(path)

        if content:
            nb = self._read_notebook(os_path, as_version=4)
            self.mark_trusted_cells(nb, path)
            model["content"] = nb
            model["format"] = "json"
            self.validate_notebook_model(model)

        return model

    def _read_file(self, gcs_path: str, format: str):
        """Read a non-notebook file.

        os_path: The path to be read.
        format:
          If 'text', the contents will be decoded as UTF-8.
          If 'base64', the raw bytes contents will be encoded as base64.
          If not specified, try to decode as UTF-8, and fall back to base64
        """
        if not self._fs.isfile(gcs_path):
            raise web.HTTPError(400, "Cannot read non-file %s" % gcs_path)

        with self._fs.open(gcs_path, "rb") as f:
            bcontent = f.read()

        if format is None or format == "text":
            # Try to interpret as unicode if format is unknown or if unicode
            # was explicitly requested.
            try:
                return bcontent.decode("utf8"), "text"
            except UnicodeError:
                if format == "text":
                    raise web.HTTPError(
                        400, "%s is not UTF-8 encoded" % gcs_path, reason="bad format",
                    )
        return encodebytes(bcontent).decode("ascii"), "base64"

    def _save_file(
        self, gcs_path: str, content: str, format: typing.Literal["text", "base64"]
    ):
        """Save content of a generic file."""
        if format not in {"text", "base64"}:
            raise web.HTTPError(
                400, "Must specify format of file contents as 'text' or 'base64'",
            )
        try:
            if format == "text":
                bcontent = content.encode("utf8")
            else:
                b64_bytes = content.encode("ascii")
                bcontent = decodebytes(b64_bytes)
        except Exception as e:
            raise web.HTTPError(400, "Encoding error saving %s: %s" % (gcs_path, e))

        with self._fs.open(gcs_path, "wb") as f:
            f.write(bcontent)

    def _save_directory(self, gcs_path: str):
        """create a directory"""
        if is_hidden(gcs_path, self.root_dir) and not self.allow_hidden:
            raise web.HTTPError(400, "Cannot create hidden directory %r" % gcs_path)
        if not self._fs.exists(
            gcs_path
        ):  # create empty "keep" file - no real directory in GCS
            self._fs.mkdir(gcs_path)
        elif not self._fs.isdir(gcs_path):
            raise web.HTTPError(400, "Not a directory: %s" % (gcs_path))
        else:
            self.log.debug("Directory %r already exists", gcs_path)
