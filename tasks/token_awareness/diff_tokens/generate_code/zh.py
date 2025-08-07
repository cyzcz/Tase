import re
import random
import csv
import os

from tqdm import tqdm


def is_chinese_char(ch):
    return '\u4e00' <= ch <= '\u9fff'


def extract_chinese_chars(text):
    return [ch for ch in text if is_chinese_char(ch)]


def compare_char_lists(list1, list2):
    if sorted(list1) == sorted(list2):
        return "是"
    l1 = list1[:]
    l2 = list2[:]
    for ch in list1:
        if ch in l2:
            l2.remove(ch)
            l1.remove(ch)
    return l1[0] if l1 else l2[0]


def create_chinese_diff_samples(input_file, output_csv):
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    chars = extract_chinese_chars(content)

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
                original_char = base[mod_index]
                replacement_char = random.choice(chars)
                while replacement_char == original_char:
                    replacement_char = random.choice(chars)
                modified = base[:]
                modified[mod_index] = replacement_char
            else:
                modified = base[:]

            variations = [
                ("不变", base, base),
                ("增加", base, base + [random.choice(chars)]),
                ("删除", base, base[:-1] if len(base) > 1 else base),
                ("修改", base, modified),  
            ]

            for label, base_seq, mod_seq in variations:
                seq1 = base_seq[:]
                seq2 = mod_seq[:]

                random.shuffle(seq1)
                random.shuffle(seq2)

                answer = compare_char_lists(seq1, seq2)

                input_text = (
                    "seq1 和 seq2 中的字是否一一完全对应（忽略顺序）？"
                    "如果是，回答“是”；如果不是，请指出不同的那个字。\n"
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

    print(f"✅ 成功生成 {len(results)} 条中文样本到 {output_csv}")



input_file = "../dataset/chinese.txt"
output_csv = "chinese.csv"

if not os.path.exists(input_file):
    print(f"❌ 错误：找不到输入文件 {input_file}")
else:
    create_chinese_diff_samples(input_file, output_csv)
