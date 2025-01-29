import json
import pathlib
import shutil

import os

from BlueprintRenderer.reference.TypeFields import Field
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

    print(f"registering {name}")

    with open(os.path.join(REFERENCE_TARGET, "types", name + ".py"), "w") as file_handle:
        file_handle.write(f'"""\nThis is an automatic generated file for the {name} type,\n'
                          f'the documentation can be found here {documentation_link}\n"""\n\n')

        if parent is not None:
            file_handle.write(f"import {parent}\n")
        file_handle.write(f"from BlueprintRenderer.reference import TypeFields\n\n")

        imports = set()
        if "properties" in json_content.keys():
            for field in json_content["properties"]:
                imports.add(Field.getFieldImport(field["type"]))
        if "" in imports:
            imports.remove("")
        if imports:
            for i in imports:
                file_handle.write(i)
            file_handle.write("\n")

        file_handle.write(f"\n")

        if parent is not None:
            file_handle.write(f"class {name}({parent}.{parent}):\n")
        else:
            file_handle.write(f"class {name}(TypeFields.StructField):\n")

        file_handle.write(f'\t"""\n')
        for line in description.split("\n"):
            file_handle.write(f'\t{line}\n')
        file_handle.write(f'\t"""\n\n')

        if isinstance(json_content["type"], dict) and "complex_type" in json_content["type"] and json_content["type"][
            "complex_type"] == "struct":
            for field in json_content["properties"]:
                optional = field["optional"]
                default = field["default"] if "default" in field.keys() else None

                file_handle.write(
                    f"\t{field['name']} = {Field.getFieldName(field['type'])}({'' if default is None else 'default_value=None, '}{'' if optional is None else 'optional=' + str(optional) + ', '})\n")

        elif isinstance(json_content["type"], str) and json_content["type"] == "string" and name.endswith("ID"):
            # ID connector
            # print("tried to register connector!")
            pass
        else:
            # print(json_content)
            # print("No matching values found!")
            pass
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
