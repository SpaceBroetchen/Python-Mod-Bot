from core.MetaObject import MetaObject


class Event(MetaObject):
    _await_register = {}
    _registered_events = {}

    @classmethod
    def registerEventHandler(cls, method, priority=None):
        if priority is None:
            priority = 0
        if priority not in cls.registered_events.keys():
            cls.registered_events[priority] = set()
        cls.registered_events[priority].add(method)

    def callEvent(self):
        keys = list(self.registered_events.keys())
        keys.sort(reverse=True)
        for priority in keys:
            for method in self.registered_events[priority]:
                if method(self) and self.Meta.cancelable:
                    return True
        return False

    class Meta:
        name = None
        cancelable = False

        def __child_registered__(self, cls):
            if cls.Meta.name is None:
                cls.Meta.name = cls.__name__

            cls.registered_events = dict()
            Event._registered_events[cls.Meta.name] = cls
            for event in Event._await_register[cls.Meta.name].keys():
                cls.registerEventHandler(event, Event._await_register[cls.Meta.name][event])


def EventHandler(event, priority=None):
    def wrapper(method):
        if isinstance(event, str) and event in Event._registered_events:
            evt = Event._registered_events[event]
            evt.registerEventHandler(method, priority)

        elif isinstance(event, str):
            if event not in Event._await_register.keys():
                Event._await_register[event] = {}
            Event._await_register[event][method] = priority

        elif issubclass(event, Event) and event != Event:
            event.registerEventHandler(method, priority)
        else:
            raise TypeError(f"event must be either a subclass of Event or a name string, not {event}!")
        return method

    return wrapper


@EventHandler("LoginEvent", 1)
def calledLoginEvent(event):
    print("blub 2")


class LoginEvent(Event):
    class Meta:
        cancelable = True


@EventHandler(LoginEvent, 5)
def calledLoginEvent(event):
    print("blub")
