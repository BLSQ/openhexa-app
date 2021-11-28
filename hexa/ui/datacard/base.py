class BaseMeta(type):
    """Metaclass for properties registration"""

    @staticmethod
    def find(attrs, of_type):
        elected = {}
        for name, instance in [
            (k, v) for k, v in attrs.items() if isinstance(v, of_type)
        ]:
            instance.name = name
            elected[name] = instance

        return elected


class DatacardComponent:
    pass
