import enum


class PipelineParameterChoicesFileFormat(enum.StrEnum):
    CSV = "csv"
    JSON = "json"
    YAML = "yaml"

    @classmethod
    def supported_extensions(cls) -> list[str]:
        return sorted({f.value for f in cls} | {"yml"})

    @classmethod
    def graphql_enum_values(cls) -> dict[str, str]:
        return {**{fmt.value: fmt.value for fmt in cls}, "yml": "yml"}

    @classmethod
    def from_extension(cls, ext: str) -> "PipelineParameterChoicesFileFormat":
        if ext == "yml":
            return cls.YAML
        try:
            return cls(ext)
        except ValueError:
            raise ValueError(
                f"Unsupported format/extension '{ext}'. "
                f"Supported: {', '.join(cls.supported_extensions())}."
            )

    @classmethod
    def from_path(cls, path: str) -> "PipelineParameterChoicesFileFormat":
        ext = path.rsplit(".", 1)[-1].lower() if "." in path else ""
        try:
            return cls.from_extension(ext)
        except ValueError:
            raise ValueError(
                f"Cannot determine file format from path '{path}'. "
                f"Supported extensions: {', '.join(cls.supported_extensions())}."
            )
