import json
import math
import os
import pathlib
import sys


def typeField(type_name=None):
    def f(cls):
        Field.add_type_field(type_name if type_name is not None else cls.__name__, cls)
        return cls

    return f


TOKENIZE_VALUES = {
    "+": "",
    "`": "",
    "''": "",
    "\"": "",
    ".": "_",
    "-": "_",
}


def modifyOutput(string):
    if string in STATIC_STRING_RESOLVE.keys():
        return STATIC_STRING_RESOLVE[string]
    else:
        return string


def tokenize(string: str) -> str:
    string = str(string)
    string = string.strip(" \t\n")
    for key, value in TOKENIZE_VALUES.items():
        string = string.replace(key, value)

    if len(string) == 0:
        return "_"
    if string[0] in "0123456789":
        string = "N" + string

    return string


with open(pathlib.Path(__file__).parent.joinpath("static_string_resolve.json").resolve()) as file_handle:
    STATIC_STRING_RESOLVE = json.load(file_handle)


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
        raise NotImplementedError(f"Cant create a literal value of abstract field! {cls.__name__}, {type_json}")

    @classmethod
    def get_parameters(cls, type_json):
        parameters = dict()
        parameters["optional"] = type_json["optional"]
        if parameters["optional"]:
            parameters["default_value"] = modifyOutput(cls.get_literal(type_json))
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

    @classmethod
    def get_literal(cls, type_json):
        if "default" not in type_json:
            return "None"
        type_json = type_json["default"]
        if isinstance(type_json, dict) and type_json["complex_type"] == "literal":
            type_json = type_json["value"]
        return f"{str(type_json)}"


@typeField("string")
class StringField(PrimitiveField):
    field_type = str

    @classmethod
    def get_literal(cls, type_json):
        return f"'{PrimitiveField.get_literal(type_json)}'"


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


class EnumField(Field):
    def __init__(self, default_value=None, optional=True, description="", options=None):
        super().__init__(default_value, optional, description)
        self.options = options

    def from_json(self, value):
        raise NotImplementedError()

    def is_valid(self, value):
        raise NotImplementedError()


@typeField("union")
class UnionField(Field):
    def __init__(self, default_value=None, optional=True, description="", options=None):
        super().__init__(default_value, optional, description)
        if options:
            self.sub_fields = options
        else:
            self.sub_fields = list()

    def from_json(self, value):
        for field in self.sub_fields:
            if field.is_valid(value):
                return field.from_json(value)

    def is_valid(self, value):
        return any([field.is_valid(value) for field in self.sub_fields])

    @classmethod
    def is_enum_field(cls, type_json):
        options = type_json["type"]["options"]
        for option in options:
            if isinstance(option, dict) and option["complex_type"] == "literal":
                continue
            return False
        return True

    @classmethod
    def get_field_imports(cls, type_json):
        if cls.is_enum_field(type_json):
            return set()
        else:
            imports = set()
            for imp in type_json["type"]["options"]:
                if isinstance(imp, str):
                    imports.add(imp)
                elif isinstance(imp, dict):
                    dummy = {
                        "type": imp,
                        "optional": False,
                        "name": ""
                    }
                    imports = imports.union(Field.get_field_pair(dummy)[0])
            return imports

    @classmethod
    def get_literal(cls, type_json):
        if cls.is_enum_field(type_json):
            if "default" in type_json.keys():
                return LiteralField.get_literal(type_json["default"])
            elif len(type_json["type"]["options"]) == 1:
                return LiteralField.get_literal(type_json["type"]["options"][0])
            else:
                return "None"

        else:
            if "default" in type_json.keys():
                if "complex_type" in type_json["default"].keys() and type_json["default"]["complex_type"] == "literal":
                    return LiteralField.get_literal(type_json["default"])

                raise NotImplementedError(f"{type_json}")
            else:
                return None

    @classmethod
    def get_field(cls, type_json):
        is_enum = cls.is_enum_field(type_json)
        if is_enum:
            field_name = "TypeFields.EnumField"
            inner_values = [LiteralField.get_literal(option) for option in type_json["type"]["options"]]
        else:
            field_name = "TypeFields.UnionField"
            inner_values = [Field.get_field_name(option) for option in type_json["type"]["options"]]

        parameters = cls.get_parameters(type_json)
        inner_options = ',\n\t\t'.join(inner_values)
        parameters["options"] = f"[\n\t\t{inner_options}\n\t]"

        parameter_string = ", ".join([f"{k}={v}" for k, v in parameters.items()])

        return f"\t{type_json['name']} = {field_name}({parameter_string})\n"


@typeField("literal")
class LiteralField(Field):
    @classmethod
    def get_field_imports(cls, type_json):
        return set()

    @classmethod
    def get_literal(cls, type_json):
        if "type" in type_json:
            type_json = type_json["type"]

        if isinstance(type_json, dict) and "complex_type" in type_json.keys() and type_json[
            "complex_type"] == "literal":
            value = type_json["value"]
            if isinstance(type_json["value"], str):
                value = f"'{value}'"

        else:
            value = type_json

        return value

    @classmethod
    def get_field(cls, type_json):
        return f"\t{type_json['name']} = {cls.get_literal(type_json)}\n"


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

    @classmethod
    def get_literal(cls, type_json):
        if "default" in type_json.keys():
            if type_json["default"] in STATIC_STRING_RESOLVE.keys():
                return STATIC_STRING_RESOLVE[type_json["default"]]

            raise Exception(type_json)
        else:
            return "[]"

class ResolvableValue:
    def resolve(self, parent):
        raise NotImplementedError


class FieldReference(ResolvableValue):
    PARENT_REFERENCE = 0

    def __init__(self, reference_name, reference_target=None):
        self.reference_name = reference_name
        self.reference_target = reference_target if reference_target is not None else FieldReference.PARENT_REFERENCE

    def resolve(self, parent):
        if self.reference_target == FieldReference.PARENT_REFERENCE:
            return parent[self.reference_name]


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

        delayed_fields = set()

        for field in self.__meta__["fields"].values():
            if field.name not in value.keys():
                if not field.optional:
                    raise Exception(f"Missing {field.name}, {field.description}")

                if isinstance(field.default_value, ResolvableValue):
                    delayed_fields.add(field.name)

                if isinstance(field, StructField):
                    setattr(instance, field.name, field.from_json(field.default_value))
                else:
                    setattr(instance, field.name, field.default_value)
                continue

            if not field.is_valid(value[field.name]):
                raise Exception(f"{value[field.name]} is not a valid value for {field.name}")

            setattr(instance, field.name, field.from_json(value[field.name]))

        for field_name in delayed_fields:
            setattr(self, field_name, getattr(self, field_name).resolve())

        instance.__meta__ = self.__meta__
        return instance

    def is_valid(self, value):
        return True

    __meta__ = {
        "fields": {}
    }

    @classmethod
    def get_literal(cls, type_json):
        if "default" in type_json:
            default = type_json["default"]
            if isinstance(default, dict) and "complex_type" in default.keys() and default["complex_type"] == "literal":
                return f"{type_json['type']}.{tokenize(default['value'])}"
            else:
                if default in STATIC_STRING_RESOLVE.keys():
                    return STATIC_STRING_RESOLVE[default]
                elif isinstance(default, str):
                    print(default)
                    return default

                else:
                    raise Exception(f"Found useful content {type_json}")
        return "None"


@typeField("dictionary")
class DictionaryField(Field):

    def __init__(self, default_value=None, optional=True, description="", keys=None, values=None):
        super().__init__(default_value, optional, description)

    def from_json(self, value):
        raise NotImplementedError()

    def is_valid(self, value):
        return super().is_valid(value)

    @classmethod
    def get_field_imports(cls, type_json):
        key_dummy = {
            "type": type_json["type"]["key"],
            "optional": False,
            "name": ""
        }
        value_dummy = {
            "type": type_json["type"]["value"],
            "optional": False,
            "name": ""
        }
        imports = Field.get_field_pair(key_dummy)[0].union(Field.get_field_pair(value_dummy)[0])
        return imports

    @classmethod
    def get_field(cls, type_json):
        field_name = cls.get_field_name(type_json["type"])

        parameters = cls.get_parameters(type_json)

        key_dummy = {
            "type": type_json["type"]["key"],
            "optional": False,
            "name": ""
        }
        value_dummy = {
            "type": type_json["type"]["value"],
            "optional": False,
            "name": ""
        }

        key = Field.get_field_pair(key_dummy)[1]
        key = "=".join(key.split("=")[1:])
        key = key.strip()
        value = Field.get_field_pair(value_dummy)[1]
        value = "=".join(value.split("=")[1:])
        value = value.strip("\n \t")
        parameters["key"] = f"{key}"
        parameters["value"] = f"{value}"

        parameter_string = ", ".join([f"{k}={v}" for k, v in parameters.items()])

        return f"\t{type_json['name']} = {field_name}({parameter_string})\n"

    @classmethod
    def get_literal(cls, type_json):
        if "default" in type_json.keys():
            raise NotImplementedError()
        else:
            return "{}"


@typeField("tuple")
class TupleField(Field):
    def __init__(self, default_value=None, optional=True, description="", values=None):
        super().__init__(default_value, optional, description)

    def from_json(self, value):
        raise NotImplementedError()

    def is_valid(self, value):
        return super().is_valid(value)

    @classmethod
    def get_field(cls, type_json):
        print(
            "Currently not implemented Tuple Field got Implemented!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        return "\tNone\n"

class PrototypeConnector(Field):
    prototype = None

