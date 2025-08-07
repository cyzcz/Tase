import re
import random
import csv
import os

from tqdm import tqdm


def is_korean_char(ch):
    return '\uac00' <= ch <= '\ud7a3'  


def extract_korean_chars(text):
    return [ch for ch in text if is_korean_char(ch)]


def compare_korean(seq1, seq2):
    if sorted(seq1) == sorted(seq2):
        return "예"  
    s1 = seq1[:]
    s2 = seq2[:]
    for ch in seq1:
        if ch in s2:
            s2.remove(ch)
            s1.remove(ch)
    return s1[0] if s1 else s2[0]


def create_korean_diff_samples(input_file, output_csv):
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    chars = extract_korean_chars(content)

    results = []

    for length in tqdm(range(5, 255)):
        max_start = len(chars) - length - 2
        if max_start < 0:
            continue

        possible_starts = list(range(0, max_start + 1))
        random.shuffle(possible_starts)
        samples_created = 0

        for start_idx in possible_starts:
            base = chars[start_idx: start_idx + length]

            
            if len(base) > 0:
                mod_index = random.randint(0, len(base) - 1)
                original = base[mod_index]
                replacement = random.choice(chars)
                while replacement == original:
                    replacement = random.choice(chars)
                modified = base[:]
                modified[mod_index] = replacement
            else:
                modified = base[:]

            variations = [
                ("unchanged", base, base),
                ("add", base, base + [random.choice(chars)]),
                ("delete", base, base[:-1] if len(base) > 1 else base),
                ("modify", base, modified),
            ]

            for label, base_seq, mod_seq in variations:
                seq1 = base_seq[:]
                seq2 = mod_seq[:]

                random.shuffle(seq1)
                random.shuffle(seq2)

                answer = compare_korean(seq1, seq2)

                input_text = (
                    "seq1과 seq2는 글자 단위로 하나하나 정확히 대응됩니까? (순서 무시)\n"
                    "맞으면 '예'라고 대답하십시오. 아니면 어떤 글자가 다른지 말하십시오.\n"
                    f"seq1: {''.join(seq1)}\n"
                    f"seq2: {''.join(seq2)}"
                )

                results.append({
                    "input": input_text,
                    "answer": answer,
                    "variation": label
                })

                samples_created += 1
                if samples_created >= 4:
                    break
            if samples_created >= 4:
                break

    
    with open(output_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["input", "answer", "variation"])
        writer.writeheader()
        writer.writerows(results)

    print(f"✅ 성공적으로 {len(results)}개의 한국어 샘플을 생성했습니다: {output_csv}")



input_file = "../dataset/korea.txt"
output_csv = "korean.csv"

if not os.path.exists(input_file):
    print(f"❌ 오류: 입력 파일을 찾을 수 없습니다: {input_file}")
else:
    create_korean_diff_samples(input_file, output_csv)
