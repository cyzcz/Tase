import random
import csv
import os


def generate_english_count_dataset(input_file, output_csv):
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            word_list = [line.strip() for line in f if line.strip()]
    except UnicodeDecodeError:
        with open(input_file, 'r', encoding='latin1') as f:
            word_list = [line.strip() for line in f if line.strip()]

    print(f"总共读取了 {len(word_list)} 个英文单词")

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

        
        total_word_count = random.randint(target_count * 10, max_total_words)
        if total_word_count <= target_count:
            continue

        
        other_words = random.choices(word_list, k=total_word_count - target_count)

        
        insert_positions = sorted(random.sample(range(len(other_words) + 1), target_count))
        for idx, pos in enumerate(insert_positions):
            other_words.insert(pos + idx, target_word)

        final_word_list = other_words
        actual_count = final_word_list.count(target_word)

        if actual_count == target_count and len(final_word_list) <= max_total_words:
            text_content = " ".join(final_word_list)
            input_text = f'How many times does "{target_word}" appear in the following text? Text: {text_content}'
            results.append({
                "text": input_text,
                "answer": str(target_count)
            })
            target_counts[target_count] += 1
            print(f"Generated {target_count}-count sample: {target_counts[target_count]}/100")

    
    with open(output_csv, 'w', encoding='utf-8', newline='') as csvfile:
        fieldnames = ['text', 'answer']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)

    print(f"✅ 数据生成完成，共写入 {len(results)} 条样本到 {output_csv}")



input_file = "../dataset/english_full.txt"
output_csv = "english.csv"

if not os.path.exists(input_file):
    print(f"文件 {input_file} 不存在，请检查路径。")
else:
    generate_english_count_dataset(input_file, output_csv)
