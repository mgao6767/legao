import os
from PIL import Image
import PIL
from collections import ChainMap
from itertools import chain
from ..legao import DIR, UPLOAD_DIR


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class LEGO(metaclass=Singleton):

    _color_names = {
        '001': 'white',
        '005': 'brick-yellow',
        '018': 'nougat',
        '021': 'bright red',
        '023': 'bright blue',
        '024': 'bright yellow',
        '026': 'black',
        '028': 'dark green',
        '037': 'bright green',
        '038': 'dark orange',
        '040': 'transparent',
        '041': 'transparent red',
        '042': 'transparent light blue',
        '043': 'transparent blue',
        '044': 'transparent yellow',
        '047': 'transparent flourescent reddish-orange',
        '048': 'transparent green',
        '049': 'transparent flourescent green',
        '102': 'medium blue',
        '106': 'bright orange',
        '111': 'transparent brown',
        '113': 'transparent medium reddish-violet',
        '119': 'bright yellowish-green',
        '124': 'bright reddish-violet',
        '126': 'transparent bright bluish-violet',
        '131': 'silver',
        '135': 'sand blue',
        '138': 'sand yellow',
        '140': 'earth blue',
        '141': 'earth green',
        '143': 'transparent flourescent blue',
        '148': 'metallic dark grey',
        '151': 'sand green',
        '154': 'dark red',
        '182': 'transparent bright orange',
        '191': 'flame yellowish orange',
        '192': 'reddish brown',
        '194': 'medium stone grey',
        '199': 'dark stone grey',
        '208': 'light stone grey',
        '212': 'light royal blue',
        '221': 'bright purple',
        '222': 'light purple',
        '226': 'cool yellow',
        '268': 'medium lilac',
        '283': 'light nougat',
        '294': 'phosph. green',
        '297': 'warm gold',
        '308': 'dark brown',
        '311': 'transparent bright green',
        '312': 'medium nougat'
    }

    _palettes = {
        'solid': {
            '024': [0xfe, 0xc4, 0x01],
            '106': [0xe7, 0x64, 0x19],
            '021': [0xde, 0x01, 0x0e],
            '221': [0xde, 0x38, 0x8b],
            '023': [0x01, 0x58, 0xa8],
            '028': [0x01, 0x7c, 0x29],
            '119': [0x95, 0xb9, 0x0c],
            '192': [0x5c, 0x1d, 0x0d],
            '018': [0xd6, 0x73, 0x41],
            '001': [0xf4, 0xf4, 0xf4],
            '026': [0x02, 0x02, 0x02],
            '226': [0xff, 0xff, 0x99],
            '222': [0xee, 0x9d, 0xc3],
            '212': [0x87, 0xc0, 0xea],
            '037': [0x01, 0x96, 0x25],
            '005': [0xd9, 0xbb, 0x7c],
            '283': [0xf5, 0xc1, 0x89],
            '208': [0xe4, 0xe4, 0xda],
            '191': [0xf4, 0x9b, 0x01],
            '124': [0x9c, 0x01, 0xc6],
            '102': [0x48, 0x8c, 0xc6],
            '135': [0x5f, 0x75, 0x8c],
            '151': [0x60, 0x82, 0x66],
            '138': [0x8d, 0x75, 0x53],
            '038': [0xa8, 0x3e, 0x16],
            '194': [0x9c, 0x92, 0x91],
            '154': [0x80, 0x09, 0x1c],
            '268': [0x2d, 0x16, 0x78],
            '140': [0x01, 0x26, 0x42],
            '141': [0x01, 0x35, 0x17],
            '312': [0xaa, 0x7e, 0x56],
            '199': [0x4d, 0x5e, 0x57],
            '308': [0x31, 0x10, 0x07]
        },

        'transparent': {
            '044': [0xf9, 0xef, 0x69],
            '182': [0xec, 0x76, 0x0e],
            '047': [0xe7, 0x66, 0x48],
            '041': [0xe0, 0x2a, 0x29],
            '113': [0xee, 0x9d, 0xc3],
            '126': [0x9c, 0x95, 0xc7],
            '042': [0xb6, 0xe0, 0xea],
            '043': [0x50, 0xb1, 0xe8],
            '143': [0xce, 0xe3, 0xf6],
            '048': [0x63, 0xb2, 0x6e],
            '311': [0x99, 0xff, 0x66],
            '049': [0xf1, 0xed, 0x5b],
            '111': [0xa6, 0x91, 0x82],
            '040': [0xee, 0xee, 0xee]
        },

        'effects': {
            '131': [0x8d, 0x94, 0x96],
            '297': [0xaa, 0x7f, 0x2e],
            '148': [0x49, 0x3f, 0x3b],
            '294': [0xfe, 0xfc, 0xd5]
        },

        'mono': {
            '001': [0xf4, 0xf4, 0xf4],
            '026': [0x02, 0x02, 0x02]
        },
    }

    def __init__(self):
        """Add an option of `all` to the palette"""
        self._palettes.update({'all': dict(ChainMap(*self.palettes.values()))})

    @property
    def palettes(self):
        return self._palettes

    @property
    def color_names(self):
        return self._color_names

    @property
    def plattes_flattened(self):
        """Convert palette mappings into color list."""
        return dict(((palette_name, list(chain(*colors.values())))
                     for palette_name, colors in self.palettes.items()))

    def brick_code_from_color(self, color):
        for brick_code, brick_color in self.palettes.get('all').items():
            if tuple(brick_color) == color:
                return brick_code

    def brick_name_from_code(self, code):
        return self._color_names.get(code)


def extend_palette(palette, colors=256, rgb=3):
    """Extend palette colors to 256 rgb sets."""
    missing_colors = colors - len(palette)//rgb
    if missing_colors > 0:
        first_color = palette[:rgb]
        palette += first_color * missing_colors
    return palette[:colors*rgb]


def apply_color_overlay(image, color):
    '''Small function to apply an effect over an entire image'''
    overlay_red, overlay_green, overlay_blue = color
    channels = image.split()

    r = channels[0].point(lambda color: overlay_effect(color, overlay_red))
    g = channels[1].point(lambda color: overlay_effect(color, overlay_green))
    b = channels[2].point(lambda color: overlay_effect(color, overlay_blue))

    channels[0].paste(r)
    channels[1].paste(g)
    channels[2].paste(b)

    return Image.merge(image.mode, channels)


def overlay_effect(color, overlay):
    '''Actual overlay effect function'''
    if color < 33:
        return overlay - 100
    elif color > 233:
        return overlay + 100
    else:
        return overlay - 133 + color


def legofy(base_image, output_path, palette_name, length=100):
    img_brick = os.path.join(DIR, '1x1.png')
    img_base = os.path.join(UPLOAD_DIR, base_image)
    with Image.open(img_base) as base, Image.open(img_brick) as brick:
        # resize base image so that its longest axis equals `length`
        base_width, base_height = base.size
        if base_width > base_height:
            new_size = (length, int(length*base_height/base_width))
        else:
            new_size = (int(base_width/base_height*length), length)
        base.thumbnail(new_size, Image.BOX)
        # get the palette
        palette = extend_palette(LEGO().plattes_flattened.get(palette_name))
        # apply effects
        palette_image = Image.new("P", (1, 1))
        palette_image.putpalette(palette)
        base = base.convert("RGB")
        base = base.quantize(palette=palette_image)
        brick_width, brick_height = brick.size
        base_width, base_height = base.size
        rbg_image = base.convert('RGB')
        lego_image = Image.new(
            "RGB", (base_width * brick_width, base_height * brick_height), "white")
        stats = {}
        for brick_x in range(base_width):
            for brick_y in range(base_height):
                color = rbg_image.getpixel((brick_x, brick_y))
                lego_image.paste(apply_color_overlay(brick, color),
                                 (brick_x * brick_width, brick_y * brick_height))
                brick_code = LEGO().brick_code_from_color(color)
                brick_count = stats.get(brick_code, 0) + 1
                stats.update({brick_code: brick_count})
        lego_image.save(output_path)
    return stats
