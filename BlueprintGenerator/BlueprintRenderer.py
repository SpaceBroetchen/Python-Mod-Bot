import base64
import json
import math
import zlib





class Blueprint:
    @staticmethod
    def decode_blueprint_string(blueprint_string):
        encoded = base64.b64decode(blueprint_string[1:])
        decoded = json.loads(zlib.decompress(encoded))
        return decoded

    def __init__(self, blueprint_string):
        self._decoded_data = Blueprint.decode_blueprint_string(blueprint_string)
        self._width = None
        self._height = None
        self._x = None
        self._y = None
        self._entity_count = None
        self._tile_count = None

    def encode(self):
        pass

    @property
    def raw_entities(self):
        if self.entity_count == 0:
            return []
        else:
            return self._decoded_data["blueprint"]["entities"]

    @property
    def raw_tiles(self):
        if self.tile_count == 0:
            return []
        else:
            return self._decoded_data["blueprint"]["tiles"]

    @property
    def width(self):
        if self._width is not None:
            return self._width

        if self.isEmpty():
            self._width = 0
            self._height = 0
            return 0

        if self.entity_count > 0:
            x_min = self.raw_entities[0]["position"]["x"]
            x_max = self.raw_entities[0]["position"]["x"]
            y_min = self.raw_entities[0]["position"]["y"]
            y_max = self.raw_entities[0]["position"]["y"]
        else:
            x_min = self.raw_tiles[0]["position"]["x"]
            x_max = self.raw_tiles[0]["position"]["x"]
            y_min = self.raw_tiles[0]["position"]["y"]
            y_max = self.raw_tiles[0]["position"]["y"]

        for i in self.raw_entities:
            if x_min > i["position"]["x"]:
                x_min = i["position"]["x"]
            if x_max < i["position"]["x"]:
                x_max = i["position"]["x"]
            if y_min > i["position"]["y"]:
                y_min = i["position"]["y"]
            if y_max < i["position"]["y"]:
                y_max = i["position"]["y"]
        for i in self.raw_tiles:
            if x_min > i["position"]["x"]:
                x_min = i["position"]["x"]
            if x_max < i["position"]["x"]:
                x_max = i["position"]["x"]
            if y_min > i["position"]["y"]:
                y_min = i["position"]["y"]
            if y_max < i["position"]["y"]:
                y_max = i["position"]["y"]

        self._x = x_min
        self._y = y_min
        self._width = x_max - x_min
        self._height = y_max - y_min
        return self._width

    def isEmpty(self):
        return self._entity_count == 0 and self._tile_count == 0

    @property
    def entity_count(self):
        if self._entity_count is None:
            if "blueprint" not in self._decoded_data or "entities" not in self._decoded_data["blueprint"]:
                self._entity_count = 0
            else:
                self._entity_count = len(self._decoded_data["blueprint"]["entities"])
        return self._entity_count

    @property
    def tile_count(self):
        if self._tile_count is None:
            if "blueprint" not in self._decoded_data or "tiles" not in self._decoded_data["blueprint"]:
                self._tile_count = 0
            else:
                self._tile_count = len(self._decoded_data["blueprint"]["tiles"])
        return self._tile_count

    @property
    def height(self):
        if self._height is None:
            self.width
        return self._height

    @property
    def x(self):
        if self._x is None:
            self.width
        return self._x

    @property
    def y(self):
        if self._y is None:
            self.width
        return self._y

    @property
    def area(self):
        return self.width * self.height

    @property
    def autoPPT(self):
        if self.isEmpty():
            return None
        return math.ceil(math.sqrt(1000000 // self.area))

    def render(self, ppt=None):
        if ppt is None:
            ppt = self.autoPPT



ts = "0eNqd1eFugyAQB/B3uc/YCIIdvEqzNNqyhUTRAF3aGN592CZdsuFS7qPm/N0J/HWBfrjo2RkbQC1gTpP1oA4LePNpu2G9Z7tRg4KPzocquM76eXKh6vUQIBIw9qyvoGh8J6BtMMHoB3C/uB3tZey1SwXkP4jAPPn07GTXjqvHd4LADVRF252IkfwBWSFIn6BIIIGzcfr0KOAZvinkmzKeF/KsjBfo1Rb51W7RIM+D+zJQPj2W997QAzZ5UKLBjQlpjX3legOkWJBugPhM1b9PJWW5BqWpqksbcHRsX2wg0MF9sQE+aVu7ukeLuZHTd94EPSbt589B4Es7f68QLZNcSiGYaBtGY/wGB7kVyg=="
ts2 = "0eNql1sGOgjAUBdB/eWtMaHkF218xLlDfTF6CxUA1MyH8u3WMM4uJJly3lNNye0vSiXbdWU6DxkRhIt33caSwmWjUz9h2t2exPQoFGuRDoxxW+Y39IEloLkjjQb4omHlbUNJO7vTUj5q0jzecR6uCvimsKpvB87n+McZYg7E1xh7ZDJbNYNkMls1g2UosW4llK7FsC1l5Z7ZZxgzI0OXA9R7L1Vi6hcxizIMfiYYz722KwzbFQf/cUsYYcxirMdZgbI0xj7Hf4wX2zVjfjPXNWN+M9c1Y34z1zVjfL1m+pmiSYx77u/UUdJFh/JnI1daz985ZV1fWzPMVM332Jg=="

print(Blueprint(ts2).autoPPT)

