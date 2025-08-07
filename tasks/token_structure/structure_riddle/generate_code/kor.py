import csv
import hgtk
from collections import defaultdict
import random


length_distribution = {
    2: 300,
    3: 250,
    4: 200,
    5: 150,
    '6+': 100
}

def get_word_length(word):
    return len([ch for ch in word if hgtk.checker.is_hangul(ch)])

def get_initials(word):
    result = []
    for ch in word:
        if hgtk.checker.is_hangul(ch):
            try:
                cho, _, _ = hgtk.letter.decompose(ch)
                result.append(cho)
            except:
                continue
    return ''.join(result)

def read_csv(filename):
    seen_english = set()
    data_by_length = defaultdict(list)

    with open(filename, encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            korean = row.get('Korean') or row.get('\ufeffKorean')
            english = row['English']
            theme = row['Theme']

            if english in seen_english:
                continue
            seen_english.add(english)

            if not korean or not theme:
                continue

            length = get_word_length(korean)
            if length >= 6:
                key = '6+'
            else:
                key = length

            data_by_length[key].append({
                'korean': korean,
                'theme': theme
            })

    return data_by_length

def build_dataset(data_by_length):
    dataset = []
    for length_key, count in length_distribution.items():
        candidates = data_by_length.get(length_key, [])
        sampled = random.sample(candidates, min(count, len(candidates)))
        for item in sampled:
            initials = get_initials(item['korean'])
            input_str = (
                "초성 퀴즈입니다!\n"
                "제시된 주제와 초성을 보고 단어를 맞혀보세요.\n"
                f"주제: {item['theme']}\n"
                f"초성: {initials}"
            )

            dataset.append({
                'input': input_str,
                'answer': item['korean'].replace(" ","")
            })
    return dataset

def save_dataset(data, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['input', 'answer'])
        writer.writeheader()
        writer.writerows(data)

def main():
    input_file = 'korean_words_with_theme.csv'
    output_file = '../korean.csv'

    data_by_length = read_csv(input_file)
    dataset = build_dataset(data_by_length)
    save_dataset(dataset, output_file)
    print(f"총 {len(dataset)}개의 퀴즈 데이터가 생성되었습니다: {output_file}")

if __name__ == "__main__":
    main()
