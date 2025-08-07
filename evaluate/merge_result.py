import os
import pandas as pd
from collections import defaultdict

# 当前目录下所有csv文件
csv_files = [f for f in os.listdir('./output_metric') if f.endswith('.csv')]

# 任务合并与映射（原始任务名 => 新任务名）
task_mapping = {
    'component_count': 'COMPC',  # Component Count
    'component_split': 'COMPM',  # Component Manipulation
    'component_split_combine': 'COMPM',  # Component Manipulation
    'diff_tokens': 'DIFF',  # Difference Identification
    'dot_matrix': 'DOT',  # Dot-Matrix Recognition
    'freq_count': 'FREQ',  # Frequency Count
    'sentence_length': 'LENOP',  # Length Operations
    'sentence_length_generate': 'LENOP',  # Length Operations
    'shuffle_tokens': 'REORD',  # Token Reordering
    'sort_lengths': 'SORT',  # Length Sorting
    'structure_riddle': 'RIDL',  # Structural Riddles
    'variant_normalize': 'VAR',  # Variant Restoration
}

# 特殊任务 dot_matrix 聚合中间变量
dot_task_records = defaultdict(lambda: {'bitmap': [], 'char': None})

# 存储每条记录：模型、任务、语言、accuracy
records = []

# 从文件中提取任务名和语言
def extract_task_and_lang(task, filename):
    fname = filename.replace('.csv', '')
    if 'generate' in fname:
        task_name = f"{task}_generate"
    elif 'combine' in fname:
        task_name = f"{task}_combine"
    else:
        task_name = task
    if 'chinese' in fname or 'zh' in fname:
        lang = 'chinese'
    elif 'english' in fname or 'en' in fname:
        lang = 'english'
    elif 'korean' in fname or 'kor' in fname:
        lang = 'korean'
    else:
        lang = 'unknown'
    return task_name, lang

# 读取所有csv文件
for file in csv_files:
    df = pd.read_csv(file)
    for _, row in df.iterrows():
        model = row['model']
        group = row['group']
        task = row['task']
        filename = row['file']
        accuracy = row['accuracy']
        task_name, lang = extract_task_and_lang(task, filename)

        # 特殊处理 dot_matrix 任务
        if task == 'dot_matrix':
            key = (model, lang)
            if 'char_classification' in filename:
                dot_task_records[key]['char'] = accuracy
            elif 'bitmap_classification_final' in filename or 'bitmap_type_classification' in filename:
                dot_task_records[key]['bitmap'].append(accuracy)
            continue  # 不加入主 records，由下方统一处理

        # 映射合并任务名
        if task in task_mapping:
            unified_task = task_mapping[task]
            records.append({
                'model': model,
                'task': unified_task,
                'language': lang,
                'accuracy': accuracy
            })

# 汇总 dot_matrix 的加权结果
for (model, lang), v in dot_task_records.items():
    if v['char'] is not None and len(v['bitmap']) > 0:
        if v['char'] == 0:
            print(f"[警告] {model}-{lang} 的 dot_matrix 中 char_classification 为 0，跳过该记录")
            continue
        bitmap_avg = sum(v['bitmap']) / len(v['bitmap'])
        adjusted_accuracy = bitmap_avg / v['char']
        records.append({
            'model': model,
            'task': 'DOT',
            'language': lang,
            'accuracy': adjusted_accuracy
        })

# 构造 DataFrame
df_all = pd.DataFrame(records)

# 第一张表：每个模型在每个任务上的平均 accuracy
task_pivot = df_all.groupby(['model', 'task'])['accuracy'].mean().unstack().reset_index()
task_pivot['average'] = task_pivot.drop(columns='model').mean(axis=1)

# 第二张表：每个模型在不同语言上的平均 accuracy
lang_pivot = df_all[df_all['language'] != 'unknown'].groupby(['model', 'language'])['accuracy'].mean().unstack().reset_index()
lang_pivot['average'] = lang_pivot.drop(columns='model').mean(axis=1)

# 输出到 Excel
with pd.ExcelWriter('model_analysis_grouped——new.xlsx') as writer:
    task_pivot.to_excel(writer, index=False, sheet_name='任务聚合')
    lang_pivot.to_excel(writer, index=False, sheet_name='语言聚合')
