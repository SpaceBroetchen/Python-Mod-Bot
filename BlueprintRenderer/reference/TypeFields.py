import os
import sys


def typeField(type_name=None):
    def f(cls):
        Field.add_type_field(type_name if type_name is not None else cls.__name__, cls)
        return cls

    return f


class Field:
    __field_registry__ = {}

    def __init__(self, default_value=None, optional=True, description=""):
        if type(self) is Field:
            raise NotImplementedError("Can't create an instance of abstract Field!")
        self.default_value = default_value
        self.optional = optional
        self.description = description

    def from_json(self, value):
        raise NotImplementedError()

    def is_valid(self, value):
        return True

    @staticmethod
    def add_type_field(name, clazz):
        Field.__field_registry__[name] = clazz

    @classmethod
    def get_field_name(cls, type_json):
        if isinstance(type_json, dict):
            type_json = type_json["complex_type"]
        if type_json not in Field.__field_registry__.keys():
            return f"{type_json}.{type_json}"
        else:
            field_class = Field.__field_registry__[type_json]
            module = ".".join(os.path.basename(sys.modules[field_class.__module__].__file__).split(".")[:-1])
            return f"{module}.{field_class.__name__}"

    @classmethod
    def get_field_imports(cls, type_json):
        type_json = type_json["type"]
        if isinstance(type_json, dict):
            type_json = type_json["complex_type"]
        if type_json not in Field.__field_registry__.keys():
            return {type_json}
        else:
            return set()

    @classmethod
    def get_literal(cls, type_json):
        return "None"

    @classmethod
    def get_parameters(cls, type_json):
        parameters = dict()
        parameters["optional"] = type_json["optional"]
        if parameters["optional"]:
            parameters["default_value"] = cls.get_literal(type_json)
        return parameters

    @classmethod
    def get_field(cls, type_json):
        field_name = Field.get_field_name(type_json['type'])
        parameters = cls.get_parameters(type_json)
        parameter_string = ", ".join([f"{k}={v}" for k, v in parameters.items()])

        return f"\t{type_json['name']} = {field_name}({parameter_string})\n"

    @staticmethod
    def get_field_pair(type_json):
        field_type = type_json["type"]
        if isinstance(field_type, dict):
            field_type = field_type["complex_type"]
        if field_type in Field.__field_registry__.keys():
            referred_field = Field.__field_registry__.get(field_type)
        else:
            referred_field = StructField

        imports = referred_field.get_field_imports(type_json)
        field_string = referred_field.get_field(type_json)
        return imports, field_string

class PrimitiveField(Field):
    field_type = None

    def from_json(self, value):
        return self.field_type(value)

    def is_valid(self, value):
        return type(value) is self.field_type


@typeField("string")
class StringField(PrimitiveField):
    field_type = str


@typeField("boolean")
@typeField("bool")
class BooleanField(PrimitiveField):
    field_type = bool


@typeField("uint8")
@typeField("uint16")
@typeField("uint32")
@typeField("uint64")
@typeField("int8")
@typeField("int16")
@typeField("int32")
@typeField("int64")
class IntegerField(PrimitiveField):
    field_type = int


@typeField("number")
@typeField("float")
@typeField("double")
class FloatField(PrimitiveField):
    field_type = float

@typeField("union")
class UnionField(Field):
    def __init__(self, default_value=None, optional=True, description="", sub_fields=None):
        super().__init__(default_value, optional, description)
        if sub_fields:
            self.sub_fields = sub_fields
        else:
            self.sub_fields = list()

    def from_json(self, value):
        for field in self.sub_fields:
            if field.is_valid(value):
                return field.from_json(value)

    def is_valid(self, value):
        return any([field.is_valid(value) for field in self.sub_fields])


@typeField("literal")
class LiteralField(UnionField):
    def __init__(self, default_value=None, optional=True, description=""):
        super().__init__(default_value, optional, description,
                         [FloatField(), IntegerField(), BooleanField(), StringField()])


@typeField("array")
class ArrayField(Field):
    def __init__(self, default_value=None, optional=True, description="", child=None):
        super().__init__(default_value, optional, description)
        self.child = child

    def from_json(self, value):
        return [self.child.from_json(i) for i in value]

    def is_valid(self, value):
        if not isinstance(value, list):
            return False
        for i in value:
            if not self.child.is_valid():
                return False


@typeField("struct")
class StructField(Field):
    def __init_subclass__(cls, scm_type=None, name=None, **kwargs):
        for i in cls.__dict__.keys():
            if isinstance(cls.__dict__[i], Field):
                cls.__meta__["fields"][i] = cls.__dict__[i]
                cls.__meta__["fields"][i].name = i

    def from_json(self, value):
        if type(self) is StructField:
            raise NotImplementedError("Can't create an instance of abstract BaseType!")

        instance = self.__class__(self.default_value, self.optional, self.description)

        for field in self.__meta__["fields"].values():
            if field.name not in value.keys():
                if not field.optional:
                    raise Exception(f"Missing {field.name}, {field.description}")
                setattr(instance, field.name, field.default_value)
                continue

            if not field.is_valid(value[field.name]):
                raise Exception(f"{value[field.name]} is not a valid value for {field.name}")

            setattr(instance, field.name, field.from_json(value[field.name]))
        instance.__meta__ = self.__meta__
        return instance

    def is_valid(self, value):
        return True

    __meta__ = {
        "fields": {}
    }

@typeField("dictionary")
class DictionaryField(Field):
