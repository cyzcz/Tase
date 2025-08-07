import os
import csv
import numpy as np
import unicodedata
from PIL import Image, ImageDraw, ImageFont


HZK_PATH = 'HZK16'
ASC_PATH = 'ASC16'
FALLBACK_FONT = 'C:/Windows/Fonts/simsun.ttc'
CHINESE_FONT = 'C:/Windows/Fonts/simsun.ttc'
ENGLISH_FONT = 'C:/Windows/Fonts/times.ttf'
KOREAN_FONT = 'C:/Windows/Fonts/malgun.ttf'
CACHE_DIR = 'cache_bitmap_csv'
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

def get_hzk16_bitmap(char, hzk_path=HZK_PATH):
    area_code = char.encode('gb2312')
    if len(area_code) != 2:
        raise ValueError("Not GB2312")
    qu = area_code[0] - 0xA1
    wei = area_code[1] - 0xA1
    offset = (94 * qu + wei) * 32
    with open(hzk_path, 'rb') as f:
        f.seek(offset)
        raw = f.read(32)
    if len(raw) != 32:
        raise ValueError("No bitmap found")
    bitmap = []
    for row in range(16):
        left = raw[row * 2]
        right = raw[row * 2 + 1]
        row_bits = (left << 8) | right
        bitmap.append([(row_bits >> (15 - i)) & 1 for i in range(16)])
    return np.array(bitmap, dtype=np.uint8)

def get_asc16_bitmap(char, asc_path=ASC_PATH):
    code = ord(char)
    if code >= 128:
        raise ValueError("Not ASCII")
    offset = code * 16
    with open(asc_path, 'rb') as f:
        f.seek(offset)
        raw = f.read(16)
    if len(raw) != 16:
        raise ValueError("No bitmap found")
    bitmap = []
    for byte in raw:
        row = [(byte >> (7 - i)) & 1 for i in range(8)]
        row = [0] * 4 + row + [0] * 4
        bitmap.append(row)
    while len(bitmap) < 16:
        bitmap.append([0] * 16)
    return np.array(bitmap, dtype=np.uint8)


def render_char_bitmap(char, font_path, size=FONT_SIZE):
    image = Image.new('L', (size, size), color=255)
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_path, size)
    bbox = font.getbbox(char)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((size - w) // 2 - bbox[0], (size - h) // 2 - bbox[1]), char, font=font, fill=0)
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

    try:
        if is_chinese(char):
            bitmap = get_hzk16_bitmap(char)
        elif ord(char) < 128:
            bitmap = get_asc16_bitmap(char)
        else:
            raise ValueError("Need fallback")
    except Exception:
        bitmap = np.zeros((16, 16), dtype=np.uint8)

    if not bitmap.any():
        if '\u4e00' <= char <= '\u9fff':
            font_path = CHINESE_FONT
        elif '\uac00' <= char <= '\ud7a3':
            font_path = KOREAN_FONT
        else:
            font_path = ENGLISH_FONT
        bitmap = render_char_bitmap(char, font_path)

    bitmap_cache[char] = bitmap
    save_to_disk_cache(char, bitmap)
    return bitmap


def load_characters_from_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    chars = [ch for ch in content if not ch.isspace()]
    return chars


def generate_csv_dataset(characters, csv_path='char_classification.csv'):
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['input', 'answer'])
        for ch in characters:
            try:
                bmp = char_to_bitmap(ch)
                label = classify_char(ch)
                if label == 'unknown':
                    continue
                question = f'''
Please classify the following character into one of the following categories:
- digit (0–9)
- latin (A–Z, a–z)
- hanzi (Chinese characters)
- hangul (Korean characters)
- kana (Japanese hiragana/katakana)
- greek (Greek letters)
- symbol (punctuation or other symbols)
character: '{ch}'
'''
                writer.writerow([question, label])
            except Exception as e:
                print(f"Skipping '{ch}': {e}")


if __name__ == "__main__":
    characters = load_characters_from_txt(CHAR_FILE)
    generate_csv_dataset(characters)
