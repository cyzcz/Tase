import os
import csv
import numpy as np
import unicodedata
from PIL import Image, ImageDraw, ImageFont


CHINESE_FONT = 'C:/Windows/Fonts/simsun.ttc'
KOREAN_FONT = 'C:/Windows/Fonts/malgun.ttf'
CACHE_DIR = 'cache_font_bitmap_16'
FONT_SIZE = 16
CHAR_FILE = '../dataset/bak.txt'

os.makedirs(CACHE_DIR, exist_ok=True)
bitmap_cache = {}


def classify_char(char):
    if char in '0123456789':
        return 'digit'
    elif 'a' <= char <= 'z' or 'A' <= char <= 'Z':
        return 'latin'
    elif '\u4e00' <= char <= '\u9fff':
        return 'hanzi'
    elif '\uac00' <= char <= '\ud7a3':
        return 'hangul'
    elif '\u3040' <= char <= '\u30ff':
        return 'kana'
    elif '\u0370' <= char <= '\u03ff':
        return 'greek'
    elif unicodedata.category(char).startswith(('P', 'S')):
        return 'symbol'
    else:
        return 'unknown'


def is_chinese(char):
    return '\u4e00' <= char <= '\u9fff'

def is_korean(char):
    return '\uAC00' <= char <= '\uD7A3'

def is_bitmap_empty(bitmap):
    return np.sum(bitmap) == 0


def render_char_bitmap(char, font_path, size=FONT_SIZE):
    image = Image.new('L', (size, size), color=255)
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_path, size)

    bbox = font.getbbox(char)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(
        ((size - w) // 2 - bbox[0], (size - h) // 2 - bbox[1]),
        char,
        font=font,
        fill=0
    )

    bw = image.point(lambda x: 1 if x < 128 else 0, mode='1')
    return np.array(bw, dtype=np.uint8)


def get_cache_path(char):
    return os.path.join(CACHE_DIR, f"U{ord(char):04X}.npy")

def load_from_disk_cache(char):
    path = get_cache_path(char)
    if os.path.exists(path):
        return np.load(path)
    return None

def save_to_disk_cache(char, bitmap):
    path = get_cache_path(char)
    np.save(path, bitmap)


def char_to_bitmap(char):
    if char in bitmap_cache:
        return bitmap_cache[char]

    cached = load_from_disk_cache(char)
    if cached is not None:
        bitmap_cache[char] = cached
        return cached

    font_path = CHINESE_FONT if is_chinese(char) else KOREAN_FONT
    bitmap = render_char_bitmap(char, font_path)

    if is_bitmap_empty(bitmap) and font_path != KOREAN_FONT:
        bitmap = render_char_bitmap(char, KOREAN_FONT)

    bitmap_cache[char] = bitmap
    save_to_disk_cache(char, bitmap)
    return bitmap


def load_characters(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return [ch for ch in content if not ch.isspace()]


def format_bitmap_for_csv(bitmap):
    return "[\n" + ",\n".join(str(list(row)) for row in bitmap) + "]"


def generate_csv(characters, output_csv='bitmap_classification_final.csv'):
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['input', 'answer'])
        for ch in characters:
            try:
                bitmap = char_to_bitmap(ch)
                label = classify_char(ch)
                if label == 'unknown':
                    continue
                bitmap_str = format_bitmap_for_csv(bitmap)
                prompt = f"Please classify the following 16x16 bitmap into the character it represents in the category ({label}):\n{bitmap_str}"
                writer.writerow([prompt, ch])
            except Exception as e:
                print(f"Skipping '{ch}': {e}")


if __name__ == '__main__':
    chars = load_characters(CHAR_FILE)
    generate_csv(chars)
