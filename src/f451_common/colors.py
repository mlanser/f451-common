"""Helper module for f451 Labs applications.

This module holds common RGB color definitions. Some color names
are repeated with different spellings to ensure compatibility with
the 'termcolor' library.

The bulk of this list is based on color codes and names found
in: https://github.com/MMVonnSeek/Python-Color-Constants-Module
"""

__all__ = [  # noqa: F822
    'COLORS'
]

#fmt: off
COLORS = {
    'aliceblue': (240, 248, 255),
    'antiquewhite': (250, 235, 215),
    'aqua': (0, 255, 255),
    'aquamarine': (127, 255, 212),
    'azure': (240, 255, 255),
    'banana': (227, 207, 87),
    'beige': (245, 245, 220),
    'bisque': (255, 228, 196),
    'black': (0, 0, 0),
    'blanchedalmond': (255, 235, 205),
    'blue': (0, 0, 255),
    'blueviolet': (138, 43, 226),
    'brick': (156, 102, 31),
    'brown': (165, 42, 42),
    'burlywood': (222, 184, 135),
    'burntsienna': (138, 54, 15),
    'burntumber': (138, 51, 36),
    'cadetblue': (95, 158, 160),
    'cadmiumorange': (255, 97, 3),
    'cadmiumyellow': (255, 153, 18),
    'carrot': (237, 145, 33),
    'chartreuse': (127, 255, 0),
    'chocolate': (210, 105, 30),
    'cobalt': (61, 89, 171),
    'cobaltgreen': (61, 145, 64),
    'coldgrey': (128, 138, 135),
    'coral': (255, 127, 80),
    'cornflowerblue': (100, 149, 237),
    'cornsilk': (255, 248, 220),
    'crimson': (220, 20, 60),
    'cyan': (0, 255, 255),
    'darkgoldenrod': (184, 134, 11),
    'darkgray': (169, 169, 169),
    'dark_gray': (169, 169, 169),
    'dark_grey': (169, 169, 169),			# Name compatible w TermColor library
    'darkgreen': (0, 100, 0),
    'darkkhaki': (189, 183, 107),
    'darkolivegreen': (85, 107, 47),
    'darkorange': (255, 140, 0),
    'darkorchid': (153, 50, 204),
    'darksalmon': (233, 150, 122),
    'darkseagreen': (143, 188, 143),
    'darkslateblue': (72, 61, 139),
    'darkslategray': (47, 79, 79),
    'darkturquoise': (0, 206, 209),
    'darkviolet': (148, 0, 211),
    'deeppink': (255, 20, 147),
    'deepskyblue': (0, 191, 255),
    'dimgray': (105, 105, 105),
    'dodgerblue': (30, 144, 255),
    'eggshell': (252, 230, 201),
    'emeraldgreen': (0, 201, 87),
    'firebrick': (178, 34, 34),
    'flesh': (255, 125, 64),
    'floralwhite': (255, 250, 240),
    'forestgreen': (34, 139, 34),
    'gainsboro': (220, 220, 220),
    'ghostwhite': (248, 248, 255),
    'gold': (255, 215, 0),
    'goldenrod': (218, 165, 32),
    'grey': (128, 128, 128),				# Name compatible w TermColor library
    'gray': (128, 128, 128),
    'green': (0, 128, 0),
    'greenyellow': (173, 255, 47),
    'honeydew': (240, 255, 240),
    'hotpink': (255, 105, 180),
    'indianred': (205, 92, 92),
    'indigo': (75, 0, 130),
    'ivory': (255, 255, 240),
    'ivoryblack': (41, 36, 33),
    'khaki': (240, 230, 140),
    'lavender': (230, 230, 250),
    'lavenderblush': (255, 240, 245),
    'lawngreen': (124, 252, 0),
    'lemonchiffon': (255, 250, 205),
    'lightblue': (173, 216, 230),
    'light_blue': (173, 216, 230),			# Name compatible w TermColor library
    'lightcoral': (240, 128, 128),
    'lightcyan': (224, 255, 255),
    'light_cyan': (224, 255, 255),			# Name compatible w TermColor library
    'lightgoldenrod': (255, 236, 139),
    'lightgoldenrodyellow': (250, 250, 210),
    'light_green': (144, 238, 144),			# Name compatible w TermColor library
    'lightgrey': (211, 211, 211),
    'light_grey': (211, 211, 211),			# Name compatible w TermColor library
    'light_magenta': (241, 178, 220),		# Name compatible w TermColor library
    'lightpink': (255, 182, 193),
    'light_red': (255, 114, 118),			# Name compatible w TermColor library
    'lightsalmon': (255, 160, 122),
    'lightseagreen': (32, 178, 170),
    'lightskyblue': (135, 206, 250),
    'lightslateblue': (132, 112, 255),
    'lightslategray': (119, 136, 153),
    'lightsteelblue': (176, 196, 222),
    'lightyellow': (255, 255, 224),
    'light_yellow': (255, 255, 224),		# Name compatible w TermColor library
    'limegreen': (50, 205, 50),
    'linen': (250, 240, 230),
    'magenta': (255, 0, 255),
    'manganeseblue': (3, 168, 158),
    'maroon': (128, 0, 0),
    'mediumorchid': (186, 85, 211),
    'mediumpurple': (147, 112, 219),
    'mediumseagreen': (60, 179, 113),
    'mediumslateblue': (123, 104, 238),
    'mediumspringgreen': (0, 250, 154),
    'mediumturquoise': (72, 209, 204),
    'mediumvioletred': (199, 21, 133),
    'melon': (227, 168, 105),
    'midnightblue': (25, 25, 112),
    'mint': (189, 252, 201),
    'mintcream': (245, 255, 250),
    'mistyrose': (255, 228, 225),
    'moccasin': (255, 228, 181),
    'navajowhite': (255, 222, 173),
    'navy': (0, 0, 128),
    'oldlace': (253, 245, 230),
    'olive': (128, 128, 0),
    'olivedrab': (107, 142, 35),
    'orange': (255, 128, 0),
    'orangered': (255, 69, 0),
    'orchid': (218, 112, 214),
    'palegoldenrod': (238, 232, 170),
    'palegreen': (152, 251, 152),
    'paleturquoise': (187, 255, 255),
    'palevioletred': (219, 112, 147),
    'papayawhip': (255, 239, 213),
    'peachpuff': (255, 218, 185),
    'peacock': (51, 161, 201),
    'pink': (255, 192, 203),
    'plum': (221, 160, 221),
    'powderblue': (176, 224, 230),
    'purple': (128, 0, 128),
    'raspberry': (135, 38, 87),
    'rawsienna': (199, 97, 20),
    'red': (255, 0, 0),
    'rosybrown': (188, 143, 143),
    'royalblue': (65, 105, 225),
    'salmon': (250, 128, 114),
    'sandybrown': (244, 164, 96),
    'sapgreen': (48, 128, 20),
    'seagreen': (84, 255, 159),
    'seashell': (255, 245, 238),
    'sepia': (94, 38, 18),
    'sgibeet': (142, 56, 142),
    'sgibrightgray': (197, 193, 170),
    'sgichartreuse': (113, 198, 113),
    'sgidarkgray': (85, 85, 85),
    'sgigray': (30, 30, 30),
    'sgilightblue': (125, 158, 192),
    'sgilightgray': (170, 170, 170),
    'sgiolivedrab': (142, 142, 56),
    'sgisalmon': (198, 113, 113),
    'sgislateblue': (113, 113, 198),
    'sgiteal': (56, 142, 142),
    'sienna': (160, 82, 45),
    'silver': (192, 192, 192),
    'skyblue': (135, 206, 235),
    'slateblue': (106, 90, 205),
    'slategray': (112, 128, 144),
    'snow': (255, 250, 250),
    'springgreen': (0, 255, 127),
    'steelblue': (70, 130, 180),
    'tan': (210, 180, 140),
    'teal': (0, 128, 128),
    'thistle': (216, 191, 216),
    'tomato': (255, 99, 71),
    'turquoise': (64, 224, 208),
    'turquoiseblue': (0, 199, 140),
    'violet': (238, 130, 238),
    'violetred': (208, 32, 144),
    'warmgrey': (128, 128, 105),
    'wheat': (245, 222, 179),
    'white': (255, 255, 255),
    'whitesmoke': (245, 245, 245),
    'yellow': (255, 255, 0),
}
#fmt: on