from hybridcontents import HybridContentsManager


class MultiContentsManager(HybridContentsManager):
    """Override a few methods from HybridContentsManager"""

    def get(self, path, content=True, type=None, format=None):
        """Nasty get() override to deal with the fact that ContentsManager.is_hidden() is not called.
        We want to ignore some files/directories at the root (notably the lost+found folder in GCS disks), but there is
        no clean solution for his at the moment. This should be fixed upstream, we need to submit a PR."""

        model = super().get(path, content, type, format)

        if path.strip("/") == "":  # ignore "lost+found" at the root
            model["content"] = [
                c for c in model["content"] if c["path"] != "lost+found"
            ]

        return model
