import random
import csv
from typing import List, Dict


def read_words_from_file(filename: str) -> List[str]:
    with open(filename, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file if line.strip()]


def split_word(word: str, min_parts: int = 2, max_parts: int = 4) -> List[str]:
    max_possible = len(word) // 2
    max_parts = min(max_parts, max_possible)
    min_parts = max(min_parts, 2)
    if max_parts < min_parts:
        min_parts = max_parts

    
    num_splits = random.randint(min_parts - 1, max_parts - 1)
    split_points = [0]
    current_min = 2

    for _ in range(num_splits):
        remaining_splits = num_splits - len(split_points) + 1
        max_pos = len(word) - 2 * remaining_splits
        if current_min > max_pos:
            break
        pos = random.randint(current_min, max_pos)
        split_points.append(pos)
        current_min = pos + 2

    split_points.append(len(word))

    
    parts = [word[split_points[i]:split_points[i + 1]] for i in range(len(split_points) - 1)]
    if any(len(p) < 2 for p in parts):
        return split_word(word, min_parts, max_parts + 1)  

    return parts


def generate_combination_task(word: str) -> Dict[str, str]:
    parts = split_word(word)
    random.shuffle(parts)
    return {
        "input": f"Combine {', '.join(f'{{{p}}}' for p in parts)} into one word.",
        "output": word
    }


def generate_splitting_task(word: str) -> Dict[str, str]:
    parts = split_word(word)
    descriptions = []
    cursor = 0

    for part in parts:
        start = cursor
        end = cursor + len(part) - 1
        descriptions.append(f"from {word[start]} to {word[end]}")
        cursor += len(part)

    return {
        "input": f"Split {word} into {', '.join(descriptions)}.",
        "output": ", ".join(parts)  
    }


def generate_datasets(words: List[str]) -> tuple:
    long_words = [w for w in words if len(w) > 5]
    selected = random.sample(long_words, min(1000, len(long_words)))

    
    dataset_a = [generate_combination_task(w) for w in selected]
    dataset_b = [generate_splitting_task(w) for w in selected]

    return dataset_a, dataset_b


def save_dataset(data: List[Dict[str, str]], filename: str) -> None:
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['input', 'output'])
        writer.writeheader()
        writer.writerows(data)


def main():
    words = read_words_from_file('../dataset/english_full.txt')
    dataset_a, dataset_b = generate_datasets(words)

    save_dataset(dataset_a, '../en_combine.csv')
    save_dataset(dataset_b, '../en_split.csv')

    print(f"数据集A生成 {len(dataset_a)} 条 (en_combine.csv)")
    print(f"数据集B生成 {len(dataset_b)} 条 (en_split.csv)")


if __name__ == "__main__":
    main()