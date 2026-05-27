import enum


class PipelineParameterChoicesFileFormat(enum.StrEnum):
    CSV = "csv"
    JSON = "json"
    YAML = "yaml"

    _ALIASES = enum.nonmember({"yml": "yaml"})

    @classmethod
    def supported_extensions(cls) -> list[str]:
        return sorted({fmt.value for fmt in cls} | cls._ALIASES.keys())

    @classmethod
    def graphql_enum_values(cls) -> dict[str, str]:
        return {**{fmt.value: fmt.value for fmt in cls}, **cls._ALIASES}

    @classmethod
    def from_extension(cls, ext: str) -> "PipelineParameterChoicesFileFormat":
        try:
            resolved_ext = cls._ALIASES.get(ext, ext)
            return cls(resolved_ext)
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
