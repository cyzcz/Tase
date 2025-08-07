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


def compare_words(seq1, seq2):
    if sorted(seq1) == sorted(seq2):
        return "yes"
    s1 = seq1[:]
    s2 = seq2[:]
    for word in seq1:
        if word in s2:
            s2.remove(word)
            s1.remove(word)
    return s1[0] if s1 else s2[0]


def create_find_diff_samples(input_file, output_csv):
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    raw_words = re.findall(r"\b[\w'-]+\b", content)
    words = [w for w in raw_words if is_valid_english_word(w)]

    results = []

    for length in tqdm(range(5, 255)):
        max_start = len(words) - length - 2
        if max_start < 0:
            continue

        possible_starts = list(range(0, max_start + 1))
        random.shuffle(possible_starts)
        samples_created = 0

        for start_idx in possible_starts:
            base = words[start_idx: start_idx + length]

            if contains_chinese(" ".join(base)):
                continue

            
            if len(base) > 0:
                mod_index = random.randint(0, len(base) - 1)
                original_word = base[mod_index]
                replacement_word = random.choice(words)
                while replacement_word == original_word:
                    replacement_word = random.choice(words)
                modified = base[:]
                modified[mod_index] = replacement_word
            else:
                modified = base[:]

            variations = [
                ("unchanged", base, base),
                ("add", base, base + [random.choice(words)]),
                ("delete", base, base[:-1] if len(base) > 1 else base),
                ("modify", base, modified),  
            ]

            for label, base_seq, mod_seq in variations:
                seq1 = base_seq[:]
                seq2 = mod_seq[:]

                random.shuffle(seq1)
                random.shuffle(seq2)

                answer = compare_words(seq1, seq2)

                input_text = (
                    f"Are the words in seq1 and seq2 exactly matching one-to-one (ignoring order)? "
                    f"If yes, answer 'yes'. If not, which word is different?\n"
                    f"seq1: {' '.join(seq1)}\n"
                    f"seq2: {' '.join(seq2)}"
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

    print(f"✅ 成功生成 {len(results)} 条样本到 {output_csv}")



input_file = "../dataset/english.txt"
output_csv = "english.csv"

if not os.path.exists(input_file):
    print(f"❌ 错误：找不到输入文件 {input_file}")
else:
    create_find_diff_samples(input_file, output_csv)
