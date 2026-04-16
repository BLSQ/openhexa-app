from uvicorn.workers import UvicornWorker


class UvicornWorkerNoLifespan(UvicornWorker):
    CONFIG_KWARGS = {**UvicornWorker.CONFIG_KWARGS, "lifespan": "off"}
