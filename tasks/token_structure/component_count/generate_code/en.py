import random
import csv

def load_words(filename):
    words = []
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            w = line.strip().lower()
            if w:
                words.append(w)
    return words

def count_letter_in_words(words, letter):
    total_count = 0
    for w in words:
        total_count += w.count(letter)
    return total_count

def generate_questions(words, questions_per_count=100):
    dataset = []
    target_counts = list(range(11))  
    letters = [chr(i) for i in range(ord('a'), ord('z')+1)]
    letter_word_map = {letter: [w for w in words if letter in w] for letter in letters}

    for target in target_counts:
        generated = 0
        attempts = 0
        
        while generated < questions_per_count:
            attempts += 1
            letter = random.choice(letters)
            candidate_words = letter_word_map[letter]

            if target == 0:
                chosen_words = random.sample(words, random.randint(1, 3))
            else:
                if len(candidate_words) < 1:
                    continue
                num_words = random.randint(1, 3)
                if len(candidate_words) < num_words:
                    continue
                chosen_words = random.sample(candidate_words, num_words)

            count = count_letter_in_words(chosen_words, letter)
            if count == target:
                question_text = f'How many times does the letter "{letter}" appear in {" ".join(chosen_words)}?'
                dataset.append((question_text, count))
                generated += 1

            
            if attempts > 1000000000:
                print(f"Warning: Too many attempts generating target={target}")
                break

    random.shuffle(dataset)
    return dataset


words = load_words('../dataset/english_full.txt')
dataset = generate_questions(words, questions_per_count=100)

with open('../english.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['input', 'answer'])
    writer.writerows(dataset)
