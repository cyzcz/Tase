import os
import csv
import json
import sys
import argparse
import pandas as pd
from tqdm import tqdm
from metrics import *

csv.field_size_limit(500 * 1024 * 1024)

def load_json_config(path: str):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def evaluate_sample(evaluation_type, question, pred, label, variation=None):
    if evaluation_type == "match_answer":
        return match_answer(question, pred, label)
    elif evaluation_type == "length":
        return sentence_length(question, pred, label)
    elif evaluation_type == "shuffle":
        result1, result2 = shuffle_tokens(question, pred, label)
        return result1 and result2
    elif evaluation_type == "split":
        return split_components(question, pred, label)
    elif evaluation_type == "number":
        return match_number(question, pred, label)
    elif evaluation_type == "diff":
        return diff_judge(question, pred, label, variation)
    else:
        raise ValueError(f"Unknown evaluation type: {evaluation_type}")

def reevaluate_all(json_configs, input_dir="output", output_dir="output_metric"):
    model_result_dict = {}

    for config_path in tqdm(json_configs, desc="Task config files"):
        task_list = load_json_config(config_path)

        for task in tqdm(task_list, desc="Tasks in config", leave=False):
            group = task["group"]
            task_name = task["task"]
            evaluation = task["evaluation"]
            files = task["files"]

            for file_path in tqdm(files, desc=f"Files for {task_name}", leave=False):
                filename = os.path.basename(file_path)

                for model in os.listdir(input_dir):
                    input_csv_path = os.path.join(input_dir, model, group, task_name, filename)
                    if not os.path.exists(input_csv_path):
                        continue

                    with open(input_csv_path, encoding='utf-8') as f:
                        print(input_csv_path)
                        reader = list(csv.DictReader(f))

                    file_total = file_correct = tag_total = tag_correct = 0
                    output_rows = []

                    for row in reader:
                        question = row["input"]
                        pred = row.get("pred", "")
                        label = row.get("answer", "").strip()
                        variation = row.get("variation", None)

                        correct_flag = ""
                        try:
                            result = evaluate_sample(evaluation, question, pred, label, variation)
                        except Exception:
                            result = None

                        if result is not None:
                            correct_flag = int(bool(result))
                            file_total += 1
                            file_correct += correct_flag
                        else:
                            correct_flag = ""

                        tag_flag = int(extract_answer(pred) != "")
                        if tag_flag:
                            tag_total += 1
                            if correct_flag == 1:
                                tag_correct += 1

                        row["correct_reeval"] = correct_flag
                        row["answer_tagged"] = tag_flag
                        output_rows.append(row)

                    acc = file_correct / file_total if file_total else 0
                    tag_acc = tag_correct / tag_total if tag_total else 0

                    result_row = {
                        "model": model,
                        "group": group,
                        "task": task_name,
                        "file": filename,
                        "accuracy": round(acc, 4),
                        "total": file_total,
                        "correct": file_correct,
                        "answer_tag_count": tag_total,
                        "tagged_accuracy": round(tag_acc, 4),
                        "tagged_correct": tag_correct
                    }

                    model_result_dict.setdefault(model, []).append(result_row)

                    output_path = os.path.join(output_dir, model, group, task_name)
                    os.makedirs(output_path, exist_ok=True)
                    output_file = os.path.join(output_path, filename)
                    with open(output_file, 'w', encoding='utf-8', newline='') as out_f:
                        writer = csv.DictWriter(out_f, fieldnames=output_rows[0].keys())
                        writer.writeheader()
                        writer.writerows(output_rows)

    os.makedirs(output_dir, exist_ok=True)
    for model, records in model_result_dict.items():
        df = pd.DataFrame(records)
        summary_path = os.path.join(output_dir, f"{model}_reeval_summary.csv")
        df.to_csv(summary_path, index=False)
        print(f"[{model}] summary saved to {summary_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", type=str, default="output", help="Input directory containing model outputs")
    parser.add_argument("--output_dir", type=str, default="output_metric", help="Output directory to save re-evaluation results")
    args = parser.parse_args()

    data_files = [
        "data/final_token_structure.json",
        "data/final_token_awareness.json"
    ]

    reevaluate_all(data_files, input_dir=args.input_dir, output_dir=args.output_dir)
