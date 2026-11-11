from pathlib import Path

from PIL import Image, ImageDraw


COLORCHECKER_SRGB = [
    (115, 82, 68),
    (194, 150, 130),
    (98, 122, 157),
    (87, 108, 67),
    (133, 128, 177),
    (103, 189, 170),
    (214, 126, 44),
    (80, 91, 166),
    (193, 90, 99),
    (94, 60, 108),
    (157, 188, 64),
    (224, 163, 46),
    (56, 61, 150),
    (70, 148, 73),
    (175, 54, 60),
    (231, 199, 31),
    (187, 86, 149),
    (8, 133, 161),
    (243, 243, 242),
    (200, 200, 200),
    (160, 160, 160),
    (122, 122, 121),
    (85, 85, 85),
    (52, 52, 52),
]


def build_colorcard(path: Path, width: int = 2560, height: int = 1440) -> None:
    image = Image.new("RGB", (width, height), (16, 16, 16))
    draw = ImageDraw.Draw(image)

    patch_width = 380
    patch_height = 270
    gap_x = 28
    gap_y = 24
    total_width = 6 * patch_width + 5 * gap_x
    total_height = 4 * patch_height + 3 * gap_y
    left = (width - total_width) // 2
    top = (height - total_height) // 2

    for index, color in enumerate(COLORCHECKER_SRGB):
        column = index % 6
        row = index // 6
        x = left + column * (patch_width + gap_x)
        y = top + row * (patch_height + gap_y)
        draw.rectangle((x, y, x + patch_width, y + patch_height), fill=color)

    image.save(path)


if __name__ == "__main__":
    build_colorcard(Path(__file__).with_name("colorcard.png"))
