import json
import os
import struct


def readString(file_handle):
    file_handle.read(1)
    size = struct.unpack_from("c", file_handle.read(1))[0][0]
    if size == 255:
        # if the first value is a full byte, read the next as an int to enable strings longer than 255 byte
        size = struct.unpack_from("<I", file_handle.read(4))[0]
    out = bytes(file_handle.read(size)).decode()
    return out


def readNextValue(file_handle):
    element_type = struct.unpack_from("Bx", file_handle.read(2))[0]

    if element_type == 0:
        return None
    elif element_type == 1:
        return struct.unpack_from("?", file_handle.read(1))[0]
    elif element_type == 2:
        return struct.unpack_from("<d", file_handle.read(8))[0]
    elif element_type == 3:
        return readString(file_handle)
    elif element_type == 4:
        size = struct.unpack_from("<I", file_handle.read(4))[0]
        array = []
        for i in range(size):
            array.append(readNextValue(file_handle))
        return array
    elif element_type == 5:
        size = struct.unpack_from("<I", file_handle.read(4))[0]

        ret = {}
        i = 0
        while i < size:
            key = readString(file_handle)
            if key != "":
                value = readNextValue(file_handle)
                ret[key] = value
                i += 1
                # sometimes there are empty keys with no values, they just get skipped,
                # since they dont count into the size of the actual dictionary

        return ret
    elif element_type == 6:
        return struct.unpack_from("<i", file_handle.read(4))[0]
    elif element_type == 7:
        return struct.unpack_from("<I", file_handle.read(4))[0]


class DataFile(dict):
    def __init__(self, file):
        super().__init__()
        if not os.path.exists(file):
            raise FileNotFoundError(f"No file {file} has been found!")
        if not os.path.isfile(file):
            raise FileNotFoundError(f"{file} is not a file!")

        with open(file, "rb") as file_handle:
            self.version = struct.unpack_from("<HHHHx", file_handle.read(9))
            out = readNextValue(file_handle)
            for i in out.keys():
                self[i] = out[i]
