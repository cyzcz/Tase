import random
import csv
import pandas as pd


mapping = {}
with open('../dataset/digit_0_9_variants.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        base = row['base_digit']
        variant = row['variant_char']
        if variant != base:  
            mapping.setdefault(base, []).append(variant)


samples_per_length = 100
all_numbers = []
for length in range(4, 14):
    for _ in range(samples_per_length):
        number = ''.join(random.choices('0123456789', k=length))
        all_numbers.append(number)


def replace_digits_with_variants(digit_str, mapping):
    new_digits = []
    for char in digit_str:
        if char in mapping:
            new_digits.append(random.choice(mapping[char]))
        else:
            new_digits.append(char)
    return ''.join(new_digits)

inputs = []
answers = []

for number in all_numbers:
    transformed = replace_digits_with_variants(number, mapping)
    prompt = (
        "The following is a numeric string where some digits have been visually confused with structurally similar Unicode characters. "
        "Please recover the original number.\nNumber: " + transformed
    )
    inputs.append(prompt)
    answers.append(number)


df = pd.DataFrame({
    'input': inputs,
    'answer': answers
})

csv_path = '../digital.csv'
df.to_csv(csv_path, index=False, encoding='utf-8')


print(df.head(10))
