import re
import random
import csv
import os
from collections import Counter


def generate_chinese_count_dataset(input_file, output_csv):
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(input_file, 'r', encoding='gbk') as f:
            content = f.read()

    
    chinese_chars = re.findall(r'[\u4e00-\u9fff]', content)
    print(f"总共提取了 {len(chinese_chars)} 个汉字")

    results = []
    target_counts = {i: 0 for i in range(1, 11)}
    max_samples_per_count = 100
    max_text_length = 500
    max_attempts = 100000

    attempts = 0
    while not all(count == max_samples_per_count for count in target_counts.values()) and attempts < max_attempts:
        attempts += 1
        
        target_char = random.choice(chinese_chars)

        
        desired_count = random.randint(1, 10)
        if target_counts[desired_count] >= max_samples_per_count:
            continue

        
        
        total_length = random.randint(desired_count*10, max_text_length)
        if total_length <= desired_count:
            continue  

        other_chars = random.choices(chinese_chars, k=total_length - desired_count)

        
        insert_positions = sorted(random.sample(range(len(other_chars) + 1), desired_count))
        for idx, pos in enumerate(insert_positions):
            other_chars.insert(pos + idx, target_char)

        final_text = ''.join(other_chars)

        actual_count = final_text.count(target_char)

        if actual_count == desired_count and len(final_text) <= max_text_length:
            input_text = f"在以下文本中，{target_char} 出现了多少次？文本：{final_text}"
            results.append({
                "text": input_text,
                "answer": str(desired_count),
            })
            target_counts[desired_count] += 1
            print(f"已生成 {desired_count} 次样本：{target_counts[desired_count]}/100")

    with open(output_csv, 'w', encoding='utf-8', newline='') as csvfile:
        fieldnames = ['text', 'answer']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow(result)

    print(f"生成完成，共写入 {len(results)} 条记录到 {output_csv}")



input_file = "../dataset/chinese.txt"
output_csv = "chinese1.csv"

if not os.path.exists(input_file):
    print(f"文件 {input_file} 不存在，请提供正确的文件路径。")
else:
    generate_chinese_count_dataset(input_file, output_csv)
