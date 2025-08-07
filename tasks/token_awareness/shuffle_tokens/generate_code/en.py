import re
import random
import csv
import os

from tqdm import tqdm


def contains_chinese(text):
    return any('\u4e00' <= ch <= '\u9fff' for ch in text)


def is_valid_english_word(word):
    if contains_chinese(word):
        return False
    return re.fullmatch(r"[a-zA-Z]+(?:[-'][a-zA-Z]+)*", word) is not None


def extract_shuffling_instructions(input_file, output_csv):
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(input_file, 'r', encoding='gbk', errors='ignore') as f:
            content = f.read()

    raw_words = re.findall(r"\b[\w'-]+\b", content)
    words = [w for w in raw_words if is_valid_english_word(w)]

    results = []

    for length in tqdm(range(5, 255)):
        samples_count = 0
        max_samples = 4
        max_start = len(words) - length
        if max_start < 0:
            continue

        possible_starts = list(range(0, max_start + 1))
        random.shuffle(possible_starts)

        for start_idx in possible_starts:
            segment = words[start_idx: start_idx + length]
            if contains_chinese(" ".join(segment)):
                continue

            prompt = (
                "Please shuffle the following words completely. "
                "Make sure that each word does not stay adjacent to its original neighbors.\n"
                f"Input: {' '.join(segment)}"
            )

            results.append({"input": prompt})
            samples_count += 1
            if samples_count >= max_samples:
                break

    
    with open(output_csv, 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['input'])
        writer.writeheader()
        writer.writerows(results)

    print(f"✅ 成功生成 {len(results)} 条 shuffle 指令样本到 {output_csv}")



input_file = "../dataset/english.txt"
output_csv = "english.csv"

if not os.path.exists(input_file):
    print(f"❌ 错误：找不到输入文件 {input_file}")
else:
    extract_shuffling_instructions(input_file, output_csv)
