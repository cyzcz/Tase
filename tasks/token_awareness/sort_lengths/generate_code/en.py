import re
import random
import csv
import os
import math

def is_valid_english_word(word):
    return re.fullmatch(r"[a-zA-Z]+(?:[-'][a-zA-Z]+)*", word) is not None

def extract_triplets_with_task_description(input_file, output_csv):
    random.seed(42)

    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(input_file, 'r', encoding='gbk', errors='ignore') as f:
            content = f.read()

    
    raw_words = re.findall(r"\b[\w'-]+\b", content)
    words = [w for w in raw_words if is_valid_english_word(w)]

    
    def get_random_sentence(length, max_attempts=10000):
        attempts = 0
        while attempts < max_attempts:
            attempts += 1
            if len(words) < length:
                return None
            start_idx = random.randint(0, len(words) - length)
            selected = words[start_idx:start_idx + length]
            if all(is_valid_english_word(w) for w in selected):
                return " ".join(selected)
        return None

    results = []
    max_attempts_per_length = 50

    for base_length in range(5, 255):
        generated = 0
        attempts = 0

        while generated < 4 and attempts < max_attempts_per_length:
            attempts += 1
            base_sentence = get_random_sentence(base_length)
            if not base_sentence:
                continue

            max_delta = base_length // 10 + 1
            delta_inc = random.randint(1, max_delta)
            delta_dec = random.randint(1, max_delta)

            alt_lengths = set()
            
            for d in [delta_dec, delta_dec + 1]:
                new_len = base_length - d
                if 1 <= new_len < base_length:
                    alt_lengths.add(new_len)
            
            for d in [delta_inc, delta_inc + 1]:
                new_len = base_length + d
                if new_len > base_length:
                    alt_lengths.add(new_len)


            alt_sentences = []
            for l in alt_lengths:
                s = get_random_sentence(l)
                if s:
                    alt_sentences.append((s, l))
                if len(alt_sentences) >= 2:
                    break

            if len(alt_sentences) < 2:
                continue

            a = base_sentence
            b, c = [s for s, _ in random.sample(alt_sentences, 2)]
            triplet = [a, b, c]
            random.shuffle(triplet)
            lengths = [len(x.split()) for x in triplet]

            if len(set(lengths)) < 3:
                continue  

            sorted_indices = sorted(range(3), key=lambda i: -lengths[i])
            label_map = ['A', 'B', 'C']
            answer = ''.join(label_map[i] for i in sorted_indices)

            input_text = (
                "Given three English sentences, sort them from longest to shortest based on the number of words.\n"
                "Output their corresponding labels in order, such as ABC, CAB, BAC, etc.\n"
                f"A: {triplet[0]}\n"
                f"B: {triplet[1]}\n"
                f"C: {triplet[2]}"
            )

            results.append({
                'input': input_text,
                'answer': answer
            })
            generated += 1

    
    with open(output_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['input', 'answer'])
        writer.writeheader()
        writer.writerows(results)

    print(f"共生成 {len(results)} 个英文三元组样本，写入文件：{output_csv}")



input_file = "../dataset/english.txt"
output_csv = "english.csv"

if not os.path.exists(input_file):
    print(f"错误：找不到输入文件 {input_file}")
else:
    extract_triplets_with_task_description(input_file, output_csv)
