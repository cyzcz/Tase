import csv
import random


banned_components = {'丿', '一', '彐', '丨', '乀', '冂', '厶', '罒'}

random.seed(42)  


chaizi = {}
with open('../dataset/chaizi-jt.txt', 'r', encoding='utf-8') as f:
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) < 2: continue

        char = parts[0]
        valid_splits = []

        
        for split in parts[1:]:
            components = split.split(' ')
            if len(components) > 4: continue
            if all(c not in banned_components for c in components):
                valid_splits.append(' '.join(components))

        
        if valid_splits:
            chaizi[char] = valid_splits[:4]


with open('../dataset/word.txt', 'r', encoding='utf-8') as f:
    chars = [line.strip() for line in f]


a_pool = []
for char in chars:
    if char in chaizi and chaizi[char]:
        entry = {
            'input': f'请将“{char}”拆分为可重新组合的基本部件.',
            'answer': ','.join(chaizi[char])
        }
        a_pool.append(entry)


b_pool = []
for char in chars:
    if char in chaizi and len(chaizi[char]) >= 2:
        comp = chaizi[char][1]  
        entry = {
            'input': f'使用“{comp}”可以组成哪个汉字？',
            'answer': char
        }
        b_pool.append(entry)



def safe_sample(pool, target_size):
    if len(pool) == 0: return []
    if len(pool) >= target_size:
        return random.sample(pool, target_size)
    
    print("ERROR")
    return (pool * (target_size // len(pool) + 1))[:target_size]



with open('../zh_split.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['input', 'answer'])
    writer.writeheader()
    writer.writerows(safe_sample(a_pool, 1000))

with open('../zh_combine.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['input', 'answer'])
    writer.writeheader()
    writer.writerows(safe_sample(b_pool, 1000))

print("数据集生成完成，已应用所有过滤规则")