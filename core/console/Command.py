from core.MetaObject import MetaObject


class Command(MetaObject):
    class Meta:
        event = None
        command = None
        alias = []
