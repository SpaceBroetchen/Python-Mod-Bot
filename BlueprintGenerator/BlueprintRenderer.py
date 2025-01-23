import base64
import json
import zlib


def render_blueprint(blueprint_string):
    encoded = base64.b64decode(blueprint_string[1:])
    print(encoded[0])
    print(encoded)
    encoded_bp = json.loads(zlib.decompress(encoded))

    print(json.dumps(encoded_bp, indent=4))

    j = json.dumps(encoded_bp)
    z = zlib.compress(j.encode(), 9)
    b = base64.b64encode(z)
    print(b)
    return encoded_bp

ts = "0eNqd1eFugyAQB/B3uc/YCIIdvEqzNNqyhUTRAF3aGN592CZdsuFS7qPm/N0J/HWBfrjo2RkbQC1gTpP1oA4LePNpu2G9Z7tRg4KPzocquM76eXKh6vUQIBIw9qyvoGh8J6BtMMHoB3C/uB3tZey1SwXkP4jAPPn07GTXjqvHd4LADVRF252IkfwBWSFIn6BIIIGzcfr0KOAZvinkmzKeF/KsjBfo1Rb51W7RIM+D+zJQPj2W997QAzZ5UKLBjQlpjX3legOkWJBugPhM1b9PJWW5BqWpqksbcHRsX2wg0MF9sQE+aVu7ukeLuZHTd94EPSbt589B4Es7f68QLZNcSiGYaBtGY/wGB7kVyg=="
print(render_blueprint(ts))
