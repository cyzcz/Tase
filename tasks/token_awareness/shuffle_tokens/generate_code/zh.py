import re
import random
import csv
import os


def is_chinese_char(ch):
    return '\u4e00' <= ch <= '\u9fff'


def extract_chinese_chars(text):
    return [ch for ch in text if is_chinese_char(ch)]


def extract_chinese_shuffle_instructions(input_file, output_csv):
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(input_file, 'r', encoding='gbk', errors='ignore') as f:
            content = f.read()

    chars = extract_chinese_chars(content)
    results = []

    for length in range(5, 255):
        samples_count = 0
        max_samples = 4
        max_start = len(chars) - length
        if max_start < 0:
            continue

        possible_starts = list(range(0, max_start + 1))
        random.shuffle(possible_starts)

        for start_idx in possible_starts:
            segment = chars[start_idx: start_idx + length]
            text = ''.join(segment)

            prompt = (
                "请完全打乱下面这些字，确保每个字的前后位置都与原句不相邻。\n"
                f"输入：{text}"
            )

            results.append({"input": prompt})
            samples_count += 1
            if samples_count >= max_samples:
                break

    
    with open(output_csv, 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['input'])
        writer.writeheader()
        writer.writerows(results)

    print(f"✅ 成功生成 {len(results)} 条中文打乱指令样本到 {output_csv}")



input_file = "../dataset/chinese.txt"
output_csv = "chinese.csv"

if not os.path.exists(input_file):
    print(f"❌ 错误：找不到输入文件 {input_file}")
else:
    extract_chinese_shuffle_instructions(input_file, output_csv)
