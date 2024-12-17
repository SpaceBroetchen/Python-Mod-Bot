from PIL import Image


COLORS = {
    "default": (221, 127, 33),
    "red": (207, 6, 0),
    "green": (23, 195, 43),
    "blue": (39, 137, 228),
    "orange": (221, 127, 33),
    "yellow": (212, 169, 19),
    "pink": (236, 89, 131),
    "purple": (123, 28, 168),
    "white": (204, 204, 204),
    "black": (25, 25, 25),
    "gray": (102, 102, 102),
    "brown": (76, 29, 0),
    "cyan": (70, 192, 181),
    "acid": (142, 194, 40),



}

def generateImage(color: str):
    if color.startswith("#"):
        cidx = int(color[1:], 16)
        rgb = (cidx // (256**2), (cidx // 256)%256 , cidx % 256)
    elif " " in color:
        rgb = [int(i) for i in color.split(" ")]
        rgb = tuple(rgb)
    elif color in COLORS.keys():
        rgb = COLORS[color]
    else:
        return None
    img = Image.new("RGB", (1024, 256), rgb)
    return img
