import json
import os
import pathlib
import shutil

from BlueprintRenderer.reference.TypeFieldsV2.TypeFieldTokens import HEADER
from configImport import FACTORIO_PROTOTYPE_API_JSON

TOKENIZE_VALUES = {
    "+": "",
    "`": "",
    "''": "",
    "\"": "",
    ".": "_",
    "-": "_",
}

REFERENCE_TARGET = pathlib.Path(__file__).parent.parent.parent.joinpath("reference", "generated2").resolve()


def tokenizeString(string):
    string = str(string)
    string = string.strip(" \t\n")
    for key, value in TOKENIZE_VALUES.items():
        string = string.replace(key, value)

    if len(string) == 0:
        return "_"
    if string[0] in "0123456789":
        string = "N" + string

    return string


def build_type_file6(json_content):
    pass


def build_files6(json_content):
    if "types" not in json_content:
        raise SyntaxError("Json File misses types tag!")

    available_types = dict()

    for type_struct in json_content["types"]:
        name = type_struct["name"]
        extends = type_struct["type"]
        available_types[name] = Field.get_type_name(extends)

    for type_struct in json_content["types"]:
        if type_struct["name"] in Field.__field_registry__.keys():
            continue
        builder = Field.get_field_type_builder(type_struct["type"], available_types)
        builder.build_child_class(os.path.join(REFERENCE_TARGET, "types", type_struct["name"] + ".py"), type_struct, available_types)


def build_files(json_content):
    if os.path.exists(REFERENCE_TARGET):
        shutil.rmtree(REFERENCE_TARGET)
    os.mkdir(REFERENCE_TARGET)
    os.mkdir(os.path.join(REFERENCE_TARGET, "types"))

    if "api_version" not in json_content:
        raise SyntaxError("Json File misses api version tag!")

    if json_content["api_version"] not in API_VERSIONS.keys():
        raise NotImplementedError(
            f"Version {json_content['api_version']} is not supported, supported versions are {tuple(API_VERSIONS.keys())}!")

    API_VERSIONS[json_content["api_version"]](json_content)


def type_field(type_name=None):
    def f(cls):
        Field.add_type_field(type_name if type_name is not None else cls.__name__, cls)
        return cls

    return f


API_VERSIONS = {
    6: build_files6
}


class Field:
    __field_registry__ = {}

    @staticmethod
    def add_type_field(name, clazz):
        Field.__field_registry__[name] = clazz

    def __init__(self, optional=False, default=None, description=""):
        self.optional = optional
        self.default = default
        self.description = description

    @classmethod
    def get_field_imports(cls, json_content):
        if Field.get_type_name(json_content) in Field.__field_registry__:
            return "BlueprintRenderer.reference.TypeFieldsV2.TypeFieldsV2"
        else:
            return Field.get_type_name(json_content)

    @staticmethod
    def prepare_child_class(file_handle, json_content, available_types):
        file_handle.write(HEADER % (json_content["name"], json_content["name"]))

    @classmethod
    def build_child_class(cls, path, json_content, available_types):
        with open(path, "w") as file_handle:
            Field.prepare_child_class(file_handle, json_content, available_types)

    @staticmethod
    def get_type_name(json_content):
        if isinstance(json_content, str):
            return json_content
        if isinstance(json_content, dict) and "complex_type" in json_content.keys():
            return json_content["complex_type"]
        return None

    @staticmethod
    def get_field_type_builder(json_content, available_types):
        name = Field.get_type_name(json_content)
        while name not in Field.__field_registry__.keys():
            if name not in available_types.keys():
                raise NotImplementedError(f"There is no field builder for {json_content}!")
            name = available_types[name]
        return Field.__field_registry__[name]


@type_field("builtin")
@type_field("DataExtendMethod")
class DataExtendMethod(Field):
    """this field does not have any functionality, it is just here to complete the api"""


@type_field("bool")
@type_field("double")
@type_field("float")
@type_field("int16")
@type_field("int32")
@type_field("int64")
@type_field("int8")
@type_field("string")
@type_field("uint16")
@type_field("uint32")
@type_field("uint64")
@type_field("uint8")
@type_field("struct")
@type_field("union")
@type_field("array")
@type_field("dictionary")
@type_field("tuple")
class BooleanField(Field):
    def __init__(self, optional=False, default=None, description=""):
        super().__init__(optional, default, description)


if __name__ == '__main__':
    with open(FACTORIO_PROTOTYPE_API_JSON, "r") as fh:
        jc = json.load(fh)
    build_files(jc)
