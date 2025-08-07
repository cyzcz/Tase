import re
import random
import csv
import os
import math

def extract_korean_triplets(input_file, output_csv):
    random.seed(42)

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            raw_content = f.read()
    except UnicodeDecodeError:
        with open(input_file, 'r', encoding='euc-kr') as f:
            raw_content = f.read()

    
    cleaned_content = ''.join([
        c for c in raw_content
        if re.match(r'[\uAC00-\uD7A3]', c) or c in [' ', ',', '，', '。', '；', ';', '：', ':', '\n']
    ])

    def get_random_sentences(length, count):
        samples = []
        attempts = 0
        max_attempts = 10000
        while len(samples) < count and attempts < max_attempts:
            attempts += 1
            start_pos = random.randint(0, len(cleaned_content) - 1)
            korean_count = 0
            end_pos = start_pos
            while end_pos < len(cleaned_content) and korean_count < length:
                if re.match(r'[\uAC00-\uD7A3]', cleaned_content[end_pos]):
                    korean_count += 1
                end_pos += 1
            if korean_count < length:
                continue
            text = cleaned_content[start_pos:end_pos].replace('\n', '')
            if re.search(r'[ ,，。；;：:\n]{3,}', text):
                continue
            if re.match(r'^[ ,，。；;：:]', text):
                continue
            actual_len = len(re.findall(r'[\uAC00-\uD7A3]', text))
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

            lengths = [len(re.findall(r'[\uAC00-\uD7A3]', x)) for x in triplet]
            if len(set(lengths)) < 3:
                continue

            sorted_indices = sorted(range(3), key=lambda i: -lengths[i])
            label_map = ['A', 'B', 'C']
            answer = ''.join(label_map[i] for i in sorted_indices)
            input_text = (
                "다음 세 문장을 한국어 글자 수 기준으로 길이순 정렬하세요 (긴 것부터 짧은 것까지).\n"
                "정답 예시: ABC, CAB, BAC 등\n"
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

    print(f"{len(results)}개의 삼중 샘플이 생성되어 {output_csv}에 저장되었습니다.")


input_file = "../dataset/korea.txt"
output_csv = "korean.csv"

if not os.path.exists(input_file):
    print(f"파일 {input_file} 이(가) 존재하지 않습니다.")
else:
    extract_korean_triplets(input_file, output_csv)
