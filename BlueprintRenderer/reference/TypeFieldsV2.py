import os
import pathlib

TOKENIZE_VALUES = {
    "+": "",
    "`": "",
    "''": "",
    "\"": "",
    ".": "_",
    "-": "_",
}

REFERENCE_TARGET = pathlib.Path(__file__).parent.parent.joinpath("reference", "generated2").resolve()

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


def buildFiles(json):
    if os.path.exists()


class Field:
    pass

