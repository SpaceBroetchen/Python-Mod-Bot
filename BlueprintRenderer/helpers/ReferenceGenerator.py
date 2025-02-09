import json
import pathlib
import shutil

import os

from BlueprintRenderer.reference.TypeFields import Field, LiteralField, typeField, UnionField, tokenize
from configImport import *

REFERENCE_TARGET = pathlib.Path(__file__).parent.parent.joinpath("reference", "generated").resolve()


def clearDefinitions():
    try:
        shutil.rmtree(REFERENCE_TARGET)
    except FileNotFoundError:
        pass

    os.mkdir(REFERENCE_TARGET)


def generateType(json_content):
    name = json_content["name"]
    description = json_content["description"]
    parent = json_content["parent"] if "parent" in json_content.keys() else None

    documentation_link = f"https://lua-api.factorio.com/latest/types/{name}.html"

    if name in Field.__field_registry__.keys():
        return ""

    with open(os.path.join(REFERENCE_TARGET, "types", name + ".py"), "w") as file_handle:
        file_handle.write(f'"""\nThis is an automatic generated file for the {name} type,\n'
                          f'the documentation can be found here {documentation_link}\n"""\n\n')

        if parent is not None:
            file_handle.write(f"import {parent}\n")
        file_handle.write(f"from BlueprintRenderer.reference import TypeFields\n\n")

        imports = set()
        fields = []

        if "properties" in json_content.keys():
            for field in json_content["properties"]:
                imp, f = Field.get_field_pair(field)
                imports = imports.union(imp)
                fields.append(f)
        if "" in imports:
            imports.remove("")
        if imports:
            for i in imports:
                file_handle.write(f"import {i}\n")
            file_handle.write("\n")

        file_handle.write(f"\n")

        if isinstance(json_content["type"], dict) and "complex_type" in json_content["type"] and (json_content["type"][
            "complex_type"] == "struct" or (json_content["type"]["complex_type"] == "union" and not UnionField.is_enum_field(json_content))):
            if parent is not None:
                file_handle.write(f"class {name}({parent}.{parent}):\n")
            else:
                file_handle.write(f"class {name}(TypeFields.StructField):\n")
        elif isinstance(json_content["type"], str) and json_content["type"] == "string" and name.endswith("ID"):
            pass
        elif isinstance(json_content["type"], dict) and "complex_type" in json_content["type"] and json_content["type"][
            "complex_type"] == "union":
            if parent is not None:
                file_handle.write(f"class {name}({parent}.{parent}):\n")
            else:
                file_handle.write(f"class {name}:\n")
        elif not isinstance(json_content["type"], dict) and json_content["type"] in Field.__field_registry__.keys():
            file_handle.write(f"class {name}(TypeFields.{Field.__field_registry__[json_content['type']]}):\n")
        elif not isinstance(json_content["type"], dict) and json_content["type"] in ("builtin",):
            pass # DataExtendMethod

        file_handle.write(f'\t"""\n')
        for line in description.split("\n"):
            file_handle.write(f'\t{line}\n')
        file_handle.write(f'\t"""\n\n')

        if isinstance(json_content["type"], dict) and "complex_type" in json_content["type"] and (json_content["type"][
            "complex_type"] == "struct" or (json_content["type"]["complex_type"] == "union" and not UnionField.is_enum_field(json_content))):

            for field in fields:
                file_handle.write(field)

        elif isinstance(json_content["type"], str) and json_content["type"] == "string" and name.endswith("ID"):
            print("tried to register connector!")
        elif isinstance(json_content["type"], dict) and "complex_type" in json_content["type"] and json_content["type"][
            "complex_type"] == "union":
            for option in json_content["type"]["options"]:
                file_handle.write(f"\t{tokenize(option['value'])} = {LiteralField.get_literal(option)}\n")
        elif not isinstance(json_content["type"], dict) and json_content["type"] in Field.__field_registry__.keys():
            pass # extending default field!
        elif not isinstance(json_content["type"], dict) and json_content["type"] in ("builtin",):
            pass # DataExtendMethod
        else:
            print(f"failed to register {json_content['name']}! {json_content['type']}")
    return f"import {name}\n"


def generateTypes(json_content):
    os.mkdir(os.path.join(REFERENCE_TARGET, "types"))
    with open(os.path.join(REFERENCE_TARGET, "types", "__init__.py"), "w") as file_handle:
        for json_type in json_content:
            file_handle.write(generateType(json_type))


def generateDefinitions():
    with open(FACTORIO_PROTOTYPE_API_JSON, "r") as file_handle:
        json_content = json.load(file_handle)

    generateTypes(json_content["types"])


if __name__ == '__main__':
    clearDefinitions()
    generateDefinitions()
