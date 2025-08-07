import re
import random
import csv
import os
import math

def extract_triplets_with_task_description(input_file, output_csv):
    random.seed(42)

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            raw_content = f.read()
    except UnicodeDecodeError:
        with open(input_file, 'r', encoding='gbk') as f:
            raw_content = f.read()

    cleaned_content = ''.join([
        c for c in raw_content
        if re.match(r'[\u4e00-\u9fff]', c) or c in [' ', ',', '，', '。', '；', ';', '：', ':', '\n']
    ])

    def get_random_sentences(length, count):
        samples = []
        attempts = 0
        max_attempts = 10000
        while len(samples) < count and attempts < max_attempts:
            attempts += 1
            start_pos = random.randint(0, len(cleaned_content) - 1)
            chinese_count = 0
            end_pos = start_pos
            while end_pos < len(cleaned_content) and chinese_count < length:
                if re.match(r'[\u4e00-\u9fff]', cleaned_content[end_pos]):
                    chinese_count += 1
                end_pos += 1
            if chinese_count < length:
                continue
            text = cleaned_content[start_pos:end_pos].replace('\n', '')
            if re.search(r'[ ,，。；;：:\n]{3,}', text):
                continue
            if re.match(r'^[ ,，。；;：:]', text):
                continue
            actual_len = len(re.findall(r'[\u4e00-\u9fff]', text))
            if actual_len == length:
                samples.append(text)
        return samples

    results = []
    max_attempts_per_length = 50  

    for base_length in range(5, 255):
        triplets_generated = 0
        attempt = 0

        while triplets_generated < 4 and attempt < max_attempts_per_length:
            attempt += 1

            base_list = get_random_sentences(base_length, 1)
            if not base_list:
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


            alt_pool = []
            for l in alt_lengths:
                alt_pool.extend(get_random_sentences(l, 2))
            if len(alt_pool) < 2:
                continue

            a = base_list[0]
            b, c = random.sample(alt_pool, 2)
            triplet = [a, b, c]
            random.shuffle(triplet)
            lengths = [len(re.findall(r'[\u4e00-\u9fff]', x)) for x in triplet]
            if len(set(lengths)) < 3:
                continue

            sorted_indices = sorted(range(3), key=lambda i: -lengths[i])
            label_map = ['A', 'B', 'C']
            answer = ''.join(label_map[i] for i in sorted_indices)
            input_text = (
                "给定三个句子，请根据它们的汉字数从长到短进行排序。\n"
                "请输出对应的顺序标签，例如：ABC、CAB、BAC 等。\n"
                f"A: {triplet[0]}\n"
                f"B: {triplet[1]}\n"
                f"C: {triplet[2]}"
            )
            results.append({'input': input_text, 'answer': answer})
            triplets_generated += 1

    with open(output_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['input', 'answer'])
        writer.writeheader()
        for r in results:
            writer.writerow(r)

    print(f"共生成 {len(results)} 个三元组样本，写入文件：{output_csv}")



input_file = "../dataset/chinese.txt"
output_csv = "chinese.csv"

if not os.path.exists(input_file):
    print(f"文件 {input_file} 不存在，请检查路径。")
else:
    extract_triplets_with_task_description(input_file, output_csv)
