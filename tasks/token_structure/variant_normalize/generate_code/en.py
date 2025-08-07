import random
import csv
import pandas as pd


with open('../dataset/english_full.txt', 'r', encoding='utf-8') as f:
    words = [line.strip() for line in f if len(line.strip()) > 3]


sampled_words = random.sample(words, min(1000, len(words)))


mapping = {}
with open('../dataset/letter_variants.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        base = row['base_letter'].lower()
        variant = row['variant']
        mapping.setdefault(base, []).append(variant)

def replace_with_variant(word, mapping):
    new_chars = []
    for char in word:
        lower_char = char.lower()
        if lower_char in mapping:
            chosen = random.choice(mapping[lower_char])
            if char.isupper():
                new_chars.append(chosen.upper())
            else:
                new_chars.append(chosen)
        else:
            new_chars.append(char)
    return ''.join(new_chars)


inputs = []
answers = []
for word in sampled_words:
    transformed = replace_with_variant(word, mapping)
    prompt = f"The following is an English word where some letters have been visually confused with structurally similar characters. Please recover the original word.\nWord: {transformed}"
    inputs.append(prompt)
    answers.append(word)


df = pd.DataFrame({
    'input': inputs,
    'answer': answers
})

csv_path = '../english.csv'
df.to_csv(csv_path, index=False, encoding='utf-8')


print(df.head(10))
