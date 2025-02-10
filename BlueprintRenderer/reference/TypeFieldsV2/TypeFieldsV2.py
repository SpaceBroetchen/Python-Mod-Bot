import json
import os
import pathlib
import shutil

from BlueprintRenderer.reference.TypeFieldsV2.TypeFieldTokens import HEADER, IMPORT, CLASS_NO_EXT, CLASS_EXT, TIDF, \
    MTL_COMMENT_DELIMITER, NDS
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

with open(pathlib.Path(__file__).parent.parent.parent.joinpath("reference",
                                                               "static_string_resolve.json").resolve()) as fh:
    STATIC_STRING_RESOLVE = json.load(fh)


def modifyOutput(string):
    if isinstance(string, str) and string in STATIC_STRING_RESOLVE.keys():
        return STATIC_STRING_RESOLVE[string]
    else:
        return string


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


def prepare_simple_class(build_ctx, json_content):
    if not Field.get_type_name(json_content["type"]) in build_ctx.loaded_types:
        prepare_simple_class(build_ctx, build_ctx.json_type_ref[Field.get_type_name(json_content["type"])])

    builder = Field.get_field_type_builder(json_content["type"], build_ctx)
    build_ctx.build_types[json_content["name"]] = builder.build_child_class(json_content, build_ctx)


def build_files6(json_content):
    if "types" not in json_content:
        raise SyntaxError("Json File misses types tag!")

    build_ctx = FileBuilderCTX(json_content, dict(), dict(), set(Field.__field_registry__.keys()), set(), dict())

    for type_struct in json_content["types"]:
        name = type_struct["name"]
        extends = type_struct["type"]
        build_ctx.available_types[name] = Field.get_type_name(extends)
        build_ctx.json_type_ref[type_struct["name"]] = type_struct
        if name not in build_ctx.loaded_types:
            build_ctx.remaining_types.add(type_struct["name"])

    for clazz in build_ctx.remaining_types.copy():
        if clazz in build_ctx.remaining_types:
            prepare_simple_class(build_ctx, build_ctx.json_type_ref[clazz])
    # for type_struct in json_content["types"]:
    #    if type_struct["name"] in Field.__field_registry__.keys():
    #        continue
    #
    #    builder = Field.get_field_type_builder(type_struct["type"], build_ctx.available_types)
    #    build_ctx.build_types[type_struct["name"]] = builder.build_child_class(type_struct, build_ctx.available_types)

    for class_name, clazz in build_ctx.build_types.items():
        clazz.write_file(os.path.join(REFERENCE_TARGET, "types", class_name + ".py"))


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


class FileBuilderCTX:
    def __init__(self, json_context, available_types, build_types, loaded_types, remaining_types, json_type_ref):
        self.json_context = json_context
        self.available_types = available_types
        self.build_types = build_types

        self.loaded_types = loaded_types
        self.remaining_types = remaining_types
        self.json_type_ref = json_type_ref


class SimpleField:
    def __init__(self, name, imports=None, optional=False, default=None, extra_fields=None):
        self.name = name
        self.imports = imports if imports else set()
        self.optional = optional
        self.default = default
        self.extra_fields = extra_fields

    def get_imports(self):
        imports = self.imports.copy()
        return imports

    def get_raw_field_list(self):
        out = list()
        if self.extra_fields is not None:
            parameters = self.extra_fields.copy()
            for k, v in parameters.items():
                if callable(v):
                    parameters[k] = v()
        else:
            parameters = dict()

        if self.optional is not None:
            parameters["optional"] = self.optional
        if self.default is not None:
            parameters["optional"] = self.default
        out.append(f"{self.name}({', '.join([k + '=' + str(v) for k, v in parameters.items()])})")
        return out

    def get_field_list(self, field_name):
        out = self.get_raw_field_list()
        out[0] = f"{field_name} = " + out[0]
        return out


class SimpleLiteralField(SimpleField):
    def __init__(self, literal):
        super().__init__("")
        self.literal = literal

    def get_imports(self):
        return set()

    def get_raw_field_list(self):
        return [str(self.literal) if not isinstance(self.literal, str) else f"\"{self.literal}\""]


class SimpleClass(SimpleField):
    def __init__(self, name, doc_name, extends=None, imports=None, description=None):
        super().__init__(name, imports)
        self.doc_name = doc_name
        self.extends = extends
        self.description = description
        self.fields = dict()

    def get_imports(self):
        imports = self.imports.copy()
        for field_name, field_value in self.fields.items():
            imports = imports.union(field_value.get_imports())
        return imports

    def write_file(self, path):
        with open(path, "w") as file_handle:
            file_handle.write(HEADER % (self.doc_name, self.doc_name))

            for imp in self.get_imports():
                file_handle.write(IMPORT % imp)

            file_handle.write("\n\n")

            if self.extends is None:
                file_handle.write(CLASS_NO_EXT % self.name)
            else:
                if not isinstance(self.extends, str):
                    ext = ", ".join(self.extends)
                else:
                    ext = self.extends
                file_handle.write(CLASS_EXT % (self.name, ext))
            file_handle.write(TIDF + MTL_COMMENT_DELIMITER + "\n" + TIDF)

            if self.description is None:
                file_handle.write(NDS + "\n")
            else:
                if not isinstance(self.extends, str):
                    dsc = self.description
                else:
                    dsc = self.description.split("\n")
                file_handle.write(("\n" + TIDF).join(dsc))

            file_handle.write("\n" + TIDF + MTL_COMMENT_DELIMITER + "\n")
            for field_name, field in self.fields.items():
                for line in field.get_field_list(field_name):
                    file_handle.write(TIDF + line + "\n")

    def add_field(self, field: SimpleField, name):
        self.fields[name] = field


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

    @classmethod
    def build_child_class(cls, json_content, build_ctx):
        raise NotImplementedError("Cant build a default field class!")

    @classmethod
    def build_child_field(cls, json_content, build_ctx):
        raise NotImplementedError("Cant build a default field!")

    @staticmethod
    def get_type_name(json_content):
        if isinstance(json_content, str):
            return json_content
        if isinstance(json_content, dict) and "complex_type" in json_content.keys():
            return json_content["complex_type"]
        return None

    @staticmethod
    def get_field_type_builder(json_content, build_ctx):
        name = Field.get_type_name(json_content)
        while name not in Field.__field_registry__.keys():
            if name not in build_ctx.available_types.keys():
                raise NotImplementedError(f"There is no field builder for {json_content}!")
            name = build_ctx.available_types[name]
        return Field.__field_registry__[name]


@type_field("builtin")
@type_field("DataExtendMethod")
class DataExtendMethod(Field):
    """this field does not have any functionality, it is just here to complete the api"""


@type_field("bool")
@type_field("union")
@type_field("dictionary")
@type_field("tuple")
class BooleanField(Field):
    def __init__(self, optional=False, default=None, description=""):
        super().__init__(optional, default, description)

    @classmethod
    def build_child_class(cls, json_content, build_ctx):
        clazz = SimpleClass(json_content["name"], json_content["name"], extends="TypeFieldsV2.BooleanField",
                            imports={"BlueprintRenderer.reference.TypeFieldsV2.TypeFieldsV2 as TypeFieldsV2"},
                            description=json_content["description"] if "default" in json_content.keys() else None)
        return clazz

    @classmethod
    def build_child_field(cls, json_content, build_ctx):
        return SimpleField("TypeFieldsV2.BooleanField",
                           imports={"BlueprintRenderer.reference.TypeFieldsV2.TypeFieldsV2 as TypeFieldsV2"},
                           optional=json_content["optional"],
                           default=str(json_content["default"]) if "default" in json_content.keys() else None)


@type_field("double")
@type_field("float")
class FloatField(Field):
    def __init__(self, optional=False, default=None, description=""):
        super().__init__(optional, default, description)

    @classmethod
    def build_child_class(cls, json_content, build_ctx):
        clazz = SimpleClass(json_content["name"], json_content["name"], extends="TypeFieldsV2.FloatField",
                            imports={"BlueprintRenderer.reference.TypeFieldsV2.TypeFieldsV2 as TypeFieldsV2"},
                            description=json_content["description"])
        return clazz

    @classmethod
    def build_child_field(cls, json_content, build_ctx):
        return SimpleField("TypeFieldsV2.FloatField",
                           imports={"BlueprintRenderer.reference.TypeFieldsV2.TypeFieldsV2 as TypeFieldsV2"},
                           optional=json_content["optional"],
                           default=str(json_content["default"]) if "default" in json_content.keys() else None)


@type_field("int16")
@type_field("int32")
@type_field("int64")
@type_field("int8")
@type_field("uint16")
@type_field("uint32")
@type_field("uint64")
@type_field("uint8")
class IntegerField(Field):
    def __init__(self, optional=False, default=None, description=""):
        super().__init__(optional, default, description)

    @classmethod
    def build_child_class(cls, json_content, build_ctx):
        clazz = SimpleClass(json_content["name"], json_content["name"], extends="TypeFieldsV2.IntegerField",
                            imports={"BlueprintRenderer.reference.TypeFieldsV2.TypeFieldsV2 as TypeFieldsV2"},
                            description=json_content["description"])
        return clazz

    @classmethod
    def build_child_field(cls, json_content, build_ctx):
        return SimpleField("TypeFieldsV2.IntegerField",
                           imports={"BlueprintRenderer.reference.TypeFieldsV2.TypeFieldsV2 as TypeFieldsV2"},
                           optional=json_content["optional"],
                           default=str(json_content["default"]) if "default" in json_content.keys() else None)


@type_field("string")
class StringField(Field):
    def __init__(self, optional=False, default=None, description=""):
        super().__init__(optional, default, description)

    @classmethod
    def build_child_class(cls, json_content, build_ctx):
        clazz = SimpleClass(json_content["name"], json_content["name"], extends="TypeFieldsV2.StringField",
                            imports={"BlueprintRenderer.reference.TypeFieldsV2.TypeFieldsV2 as TypeFieldsV2"},
                            description=json_content["description"])
        return clazz

    @classmethod
    def build_child_field(cls, json_content, build_ctx):
        return SimpleField("TypeFieldsV2.StringField",
                           imports={"BlueprintRenderer.reference.TypeFieldsV2.TypeFieldsV2 as TypeFieldsV2"},
                           optional=json_content["optional"],
                           default=f"\"{json_content['default']}\"" if "default" in json_content.keys() else None)


@type_field("array")
class ArrayField(Field):
    def __init__(self, optional=False, default=None, description="", values=None):
        super().__init__(optional, default, description)
        self.values = values

    @classmethod
    def build_child_class(cls, json_content, build_ctx):
        clazz = SimpleClass(json_content["name"], json_content["name"], extends="TypeFieldsV2.ArrayField",
                            imports={"BlueprintRenderer.reference.TypeFieldsV2.TypeFieldsV2 as TypeFieldsV2"},
                            description=json_content["description"])
        values = Field.get_type_name(json_content["type"]["value"])
        if values not in build_ctx.loaded_types:
            prepare_simple_class(build_ctx, build_ctx.json_type_ref[values])  # load missing child field!

        dummy_field = {
            "name": "values",
            "optional": False,
            "type": values
        }

        values_field = Field.get_field_type_builder(values, build_ctx).build_child_field(dummy_field, build_ctx)
        clazz.add_field(values_field, "values")

        return clazz

    @classmethod
    def build_child_field(cls, json_content, build_ctx):
        if isinstance(json_content["type"], str):
            # handling inherited arrays
            return SimpleField("TypeFieldsV2.FloatField",
                               imports={"BlueprintRenderer.reference.TypeFieldsV2.TypeFieldsV2 as TypeFieldsV2"},
                               optional=json_content["optional"],
                               default=f"\"{json_content['default']}\"" if "default" in json_content.keys() else None)

        values = Field.get_type_name(json_content["type"]["value"])
        #if values not in build_ctx.loaded_types:
        #    prepare_simple_class(build_ctx, build_ctx.json_type_ref[values])  # load missing child field!

        dummy_field = {
            "name": "values",
            "optional": False,
            "type": values
        }

        values_field = Field.get_field_type_builder(values, build_ctx).build_child_field(dummy_field, build_ctx)

        def c():
            return "\n".join(values_field.get_raw_field_list())


        field = SimpleField("TypeFieldsV2.StringField",
                            imports={"BlueprintRenderer.reference.TypeFieldsV2.TypeFieldsV2 as TypeFieldsV2"},
                            optional=json_content["optional"],
                            default=f"\"{json_content['default']}\"" if "default" in json_content.keys() else None,
                            extra_fields={"values": c})


@type_field("struct")
class StructField(Field):
    def __init__(self, optional=False, default=None, description=""):
        super().__init__(optional, default, description)

    @classmethod
    def build_child_class(cls, json_content, build_ctx):
        print(json_content)

        extension = Field.get_type_name(json_content["type"])
        if extension == "struct":
            imports = {"BlueprintRenderer.reference.TypeFieldsV2.TypeFieldsV2 as TypeFieldsV2"}
            extension = "TypeFieldsV2.StructField"
        else:
            imports = {extension}
            extension = "{extension}.{extension}"

        clazz = SimpleClass(json_content["name"], json_content["name"], extends=extension,
                            imports=imports,
                            description=json_content["description"])

        for sub_field in json_content["properties"]:
            sub_field_type = Field.get_type_name(sub_field["type"])

            if sub_field_type not in build_ctx.loaded_types:
                prepare_simple_class(build_ctx, build_ctx.json_type_ref[sub_field_type])  # load missing child field!

            sub_field_obj = Field.get_field_type_builder(sub_field_type, build_ctx).build_child_field(sub_field,
                                                                                                      build_ctx)
            clazz.add_field(sub_field_obj, sub_field["name"])

    @classmethod
    def build_child_field(cls, json_content, build_ctx):
        # TODO: change method signature!
        return SimpleField("TypeFieldsV2.FloatField",
                           imports={"BlueprintRenderer.reference.TypeFieldsV2.TypeFieldsV2 as TypeFieldsV2"},
                           optional=json_content["optional"],
                           default=f"\"{json_content['default']}\"" if "default" in json_content.keys() else None)


@type_field("literal")
class LiteralField(Field):
    @classmethod
    def build_child_field(cls, json_content, build_ctx):
        field = SimpleLiteralField(json_content["type"]["value"])
        return field


if __name__ == '__main__':
    with open(FACTORIO_PROTOTYPE_API_JSON, "r") as fh:
        jc = json.load(fh)
    build_files(jc)
