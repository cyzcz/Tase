import random
import csv
import os


def generate_korean_count_dataset(input_file, output_csv):
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            word_list = [line.strip() for line in f if line.strip()]
    except UnicodeDecodeError:
        with open(input_file, 'r', encoding='euc-kr') as f:
            word_list = [line.strip() for line in f if line.strip()]

    print(f"총 {len(word_list)}개의 한국어 단어를 불러왔습니다.")

    results = []
    target_counts = {i: 0 for i in range(1, 11)}
    max_samples_per_count = 100
    max_total_words = 500
    max_attempts = 100000

    attempts = 0
    while not all(v == max_samples_per_count for v in target_counts.values()) and attempts < max_attempts:
        attempts += 1

        target_word = random.choice(word_list)
        target_count = random.randint(1, 10)

        if target_counts[target_count] >= max_samples_per_count:
            continue

        total_word_count = random.randint(target_count + 10, max_total_words)
        if total_word_count <= target_count:
            continue

        other_words = random.choices(word_list, k=total_word_count - target_count)

        insert_positions = sorted(random.sample(range(len(other_words) + 1), target_count))
        for idx, pos in enumerate(insert_positions):
            other_words.insert(pos + idx, target_word)

        final_words = other_words
        actual_count = final_words.count(target_word)

        if actual_count == target_count and len(final_words) <= max_total_words:
            text_body = "".join(final_words)
            input_text = f'다음 문장에서 "{target_word}"는 몇 번 나타납니까? 문장: {text_body}'
            results.append({
                "text": input_text,
                "answer": str(target_count)
            })
            target_counts[target_count] += 1
            print(f"{target_count}회 샘플 생성됨: {target_counts[target_count]}/100")

    
    with open(output_csv, 'w', encoding='utf-8', newline='') as csvfile:
        fieldnames = ['text', 'answer']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)

    print(f"✅ 총 {len(results)}개의 샘플을 {output_csv}에 저장했습니다.")



input_file = "../dataset/korea_word.txt"
output_csv = "korean.csv"

if not os.path.exists(input_file):
    print(f"파일 {input_file}이 존재하지 않습니다. 경로를 확인하세요.")
else:
    generate_korean_count_dataset(input_file, output_csv)
