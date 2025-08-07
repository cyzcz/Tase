import re
import random
import csv
import os

def extract_chinese_samples(input_file, output_csv):
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        
        with open(input_file, 'r', encoding='gbk') as f:
            content = f.read()

    
    cleaned_content = ''
    for char in content:
        if re.match(r'[\u4e00-\u9fff]', char) or char in [' ', ',', '，', '。', '；', ';', '：', ':', '\n']:
            cleaned_content += char

    results = []

    
    for length in range(5, 255):
        samples_count = 0
        attempts = 0
        max_attempts = 1000

        while samples_count < 4 and attempts < max_attempts:
            attempts += 1

            if len(cleaned_content) == 0:
                continue
            start_pos = random.randint(0, len(cleaned_content) - 1)

            
            chinese_count = 0
            end_pos = start_pos
            while end_pos < len(cleaned_content) and chinese_count < length:
                if re.match(r'[\u4e00-\u9fff]', cleaned_content[end_pos]):
                    chinese_count += 1
                end_pos += 1

            if chinese_count < length:
                continue

            
            extracted_text = cleaned_content[start_pos:end_pos].replace('\n', '')

            
            if re.search(r'[ ,，。；;：:]{3,}', extracted_text):
                continue
            if re.match(r'^[ ,，。；;：:]', extracted_text):
                continue

            
            actual_chinese_count = len(re.findall(r'[\u4e00-\u9fff]', extracted_text))
            if actual_chinese_count == length:
                question = f"这个句子中有多少个汉字（不计算标点符号）？句子是：‘{extracted_text}’"
                results.append({
                    "input": question,
                    "answer": str(length),
                })
                samples_count += 1
                print(f"为长度 {length} 找到第 {samples_count}/5 个样本")

    
    with open(output_csv, 'w', encoding='utf-8', newline='') as csvfile:
        fieldnames = ['input', 'answer']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow(result)

    print(f"生成完成，共写入 {len(results)} 条记录到 {output_csv}")



input_file = "../dataset/chinese.txt"
output_csv = "chinese.csv"

if not os.path.exists(input_file):
    print(f"文件 {input_file} 不存在，请提供正确的文件路径。")
else:
    extract_chinese_samples(input_file, output_csv)
