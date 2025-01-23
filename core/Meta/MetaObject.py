class MetaData:
    def __init__(self, main, parents):
        self._main = main
        self._parents = parents

    def __getattr__(self, item):
        if hasattr(self._main, item):
            return getattr(self._main, item)
        for parent in self._parents:
            try:
                return getattr(parent, item)
            except AttributeError:
                continue
        raise AttributeError

    def __dir__(self):
        attributes = set(dir(self._main))
        for parent in self._parents:
            attributes.update(dir(parent))
        return list(attributes)

    def __child_registered__(self, cls):
        if cls.Meta != self and hasattr(self._main, "__child_registered__"):
            getattr(self._main, "__child_registered__")(self._main, cls)
        for parent in self._parents:
            parent.__child_registered__(cls)

class MetaClass(type):
    def __init__(cls, name, parents, attributes):
        if name == "MetaObject":
            super().__init__(name, parents, attributes)
            return

        meta_parents = list()
        for parent in parents:
            if issubclass(parent, MetaObject):
                meta_parents.append(parent.Meta)

        attributes["Meta"] = MetaData(attributes.get("Meta"), meta_parents)

        super().__init__(name, parents, attributes)
        cls.Meta = attributes["Meta"]
        cls.Meta.__child_registered__(cls)

class MetaObject(object, metaclass=MetaClass):
    Meta = MetaData(None, [])
