import random
import csv
import hgtk


def read_hangul_chars(filename: str) -> list:
    valid_chars = []
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            char = line.strip()
            if len(char) == 1 and is_valid_hangul(char):
                valid_chars.append(char)
    return valid_chars


def is_valid_hangul(char: str) -> bool:
    try:
        hgtk.letter.decompose(char)
        return True
    except:
        return False


def generate_decomposition_task(char: str) -> dict:
    cho, jung, jong = hgtk.letter.decompose(char)
    components = [cho, jung]
    if jong:  
        components.append(jong)
    return {
        "input": f"'{char}'의 초성, 중성, 종성(있는 경우)은 무엇인가요? 쉼표로 구분하세요.",
        "output": ", ".join(components)
    }


def generate_composition_task(char: str) -> dict:
    cho, jung, jong = hgtk.letter.decompose(char)
    parts = [cho, jung]
    if jong:  
        parts.append(jong)

    
    
    return {
        "input": f"다음 자모를 조합하세요: {', '.join(parts)}",
        "output": char
    }


def generate_datasets(chars: list) -> tuple:
    dataset_a = [generate_decomposition_task(c) for c in chars]
    dataset_b = [generate_composition_task(c) for c in chars]
    return dataset_a, dataset_b


def save_dataset(data: list, filename: str):
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['input', 'output'])
        writer.writeheader()
        writer.writerows(data)


def main():
    
    chars = read_hangul_chars('../dataset/korea.txt')
    selected = random.sample(chars, min(1000, len(chars)))

    
    decomp_data, comp_data = generate_datasets(selected)

    
    save_dataset(decomp_data, '../kor_split.csv')
    save_dataset(comp_data, '../kor_combine.csv')

    print(f"생성된 분해 데이터: {len(decomp_data)}개 (kor_split.csv)")
    print(f"생성된 조합 데이터: {len(comp_data)}개 (kor_combine.csv)")


if __name__ == "__main__":
    main()