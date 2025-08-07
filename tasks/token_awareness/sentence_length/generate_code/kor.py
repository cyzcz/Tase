import re
import random
import csv
import os


def extract_korean_samples(input_file, output_csv):
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(input_file, 'r', encoding='euc-kr') as f:
            content = f.read()

    
    cleaned_content = ''
    for char in content:
        if re.match(r'[\uAC00-\uD7A3]', char) or char in [' ', ',', '，', '。', '；', ';', '：', ':', '\n']:
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

            korean_count = 0
            end_pos = start_pos
            while end_pos < len(cleaned_content) and korean_count < length:
                if re.match(r'[\uAC00-\uD7A3]', cleaned_content[end_pos]):
                    korean_count += 1
                end_pos += 1

            if korean_count < length:
                continue

            extracted_text = cleaned_content[start_pos:end_pos].replace('\n', '')
            actual_korean_count = len(re.findall(r'[\uAC00-\uD7A3]', extracted_text))
            if re.search(r'[ ,，。；;：:\n]{3,}', extracted_text):
                continue
            if re.match(r'^[ ,，。；;：:]', extracted_text):
                continue

            if actual_korean_count == length:
                question = f"이 문장에는 한글 문자가 몇 개 있나요? 문장은: ‘{extracted_text}’"
                results.append({
                    "input": question,
                    "answer": str(length)
                })
                samples_count += 1
                print(f"길이 {length}에 대해 {samples_count}/5 샘플 찾음")

    
    with open(output_csv, 'w', encoding='utf-8', newline='') as csvfile:
        fieldnames = ['input', 'answer']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"완료: 총 {len(results)} 개의 QA 샘플이 {output_csv}에 저장되었습니다.")



input_file = "../dataset/korea.txt"
output_csv = "korean.csv"

if not os.path.exists(input_file):
    print(f"파일 {input_file} 이(가) 존재하지 않습니다. 올바른 경로를 입력하세요.")
else:
    extract_korean_samples(input_file, output_csv)
