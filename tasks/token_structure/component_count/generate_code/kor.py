import csv
import random
import hgtk
from collections import defaultdict
from tqdm import tqdm


def is_valid_hangul(char: str) -> bool:
    try:
        hgtk.letter.decompose(char)
        return True
    except:
        return False


def read_hangul_chars(filename: str) -> list:
    valid_chars = []
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            char = line.strip()
            if len(char) == 1 and is_valid_hangul(char):
                valid_chars.append(char)
    return valid_chars


def build_hangul_data(chars: list):
    data = {}
    for char in chars:
        try:
            parts = hgtk.letter.decompose(char)
            counts = defaultdict(int)
            for p in parts:
                if p != '':
                    counts[p] += 1
            data[char] = dict(counts)
        except:
            continue
    return data


def build_index(data):
    component_map = defaultdict(list)
    negative_map = defaultdict(list)
    all_components = set()

    for char, parts in data.items():
        for p in parts:
            component_map[p].append((char, parts[p]))
            all_components.add(p)
        for component in all_components:
            if component not in parts:
                negative_map[component].append(char)

    return component_map, negative_map, list(all_components)


def find_combination(candidates, target):
    max_attempts = 100
    for _ in range(max_attempts):
        selected = []
        current_sum = 0
        temp_candidates = candidates.copy()

        while temp_candidates and current_sum < target and len(selected) < 6:
            char, cnt = random.choice(temp_candidates)
            if current_sum + cnt > target:
                continue
            selected.append((char, cnt))
            current_sum += cnt
            temp_candidates.remove((char, cnt))

            if current_sum == target:
                return selected
    return None


def generate_question_with_k(component, component_map, negative_map, data, k):
    candidates = component_map.get(component, [])
    if not candidates:
        return None

    positive_comb = find_combination(candidates.copy(), k)
    if not positive_comb:
        return None

    m = len(positive_comb)
    remain = random.randint(0, 6 - m)

    negative_candidates = negative_map.get(component, [])
    if remain > 0:
        if len(negative_candidates) < remain:
            return None
        try:
            negative_selected = random.sample(negative_candidates, remain)
        except ValueError:
            return None
    else:
        negative_selected = []

    all_chars = [char for char, _ in positive_comb] + negative_selected
    random.shuffle(all_chars)

    if 1 <= len(all_chars) <= 6 and sum(cnt for _, cnt in positive_comb) == k:
        return (f'"{"".join(all_chars)}"에서 "{component}"는 몇 회 출현하였습니까?', k)
    return None


def generate_dataset_fixed_distribution(data):
    component_map, negative_map, all_components = build_index(data)
    dataset = []
    target_distribution = {0: 100, 1: 180, 2: 180, 3: 180, 4: 180, 5: 180}
    count_distribution = {k: 0 for k in target_distribution}

    for k in range(1, 6):
        while count_distribution[k] < target_distribution[k]:
            component = random.choice(all_components)
            question = generate_question_with_k(component, component_map, negative_map, data, k)
            if question:
                dataset.append(question)
                count_distribution[k] += 1

    while count_distribution[0] < target_distribution[0]:
        component = random.choice(all_components)
        candidates = negative_map.get(component, [])
        if not candidates:
            continue

        m = random.randint(1, min(6, len(candidates)))
        try:
            selected = random.sample(candidates, m)
            dataset.append((f'"{"".join(selected)}"에서 "{component}"는 몇 회 출현하였습니까?', 0))
            count_distribution[0] += 1
        except ValueError:
            continue

    random.shuffle(dataset)
    return dataset



chars = read_hangul_chars('korea.txt')
data = build_hangul_data(chars)
dataset = generate_dataset_fixed_distribution(data)

with open('../korean.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['input', 'answer'])
    writer.writerows(dataset)
