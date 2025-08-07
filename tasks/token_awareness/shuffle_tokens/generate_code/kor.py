import re
import random
import csv
import os


def is_korean_char(ch):
    return '\uac00' <= ch <= '\ud7a3'  


def extract_korean_chars(text):
    return [ch for ch in text if is_korean_char(ch)]


def extract_korean_shuffle_instructions(input_file, output_csv):
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(input_file, 'r', encoding='cp949', errors='ignore') as f:
            content = f.read()

    chars = extract_korean_chars(content)
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
                "다음 글자들을 완전히 섞어 주세요. "
                "각 글자가 원래 이웃한 글자들과 더 이상 인접하지 않도록 해 주세요.\n"
                f"입력: {text}"
            )

            results.append({"input": prompt})
            samples_count += 1
            if samples_count >= max_samples:
                break

    
    with open(output_csv, 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['input'])
        writer.writeheader()
        writer.writerows(results)

    print(f"✅ 총 {len(results)}개의 한글 섞기 지시 샘플을 생성했습니다: {output_csv}")



input_file = "../dataset/korea.txt"
output_csv = "korean.csv"

if not os.path.exists(input_file):
    print(f"❌ 오류: 입력 파일이 존재하지 않습니다: {input_file}")
else:
    extract_korean_shuffle_instructions(input_file, output_csv)
