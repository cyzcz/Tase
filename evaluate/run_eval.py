import os
import csv
import json
import yaml
import argparse
import pandas as pd
from tqdm import tqdm
from metrics import *
from init_model import init_model
from call_model import call_model_batch


def load_json_config(path: str):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_yaml_config(path: str = "config.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


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


def evaluate_all(json_configs, yaml_config_path="config.yaml", output_csv=None, max_eval=1500):
    config = load_yaml_config(yaml_config_path)
    provider = config["provider"]
    model_name = config["model"]
    sampling = config["sampling"]
    system_prompt = sampling.get("system_prompt", "You are a helpful assistant.")
    threads = config.get("api", {}).get("threads", 1) if provider == "api" else 1

    options = {}
    if provider == "api":
        options["api_key"] = config["api"]["api_key"]
        options["base_url"] = config["api"]["base_url"]
    model_obj = init_model(provider=provider, model=model_name, options=options)

    results = []
    task_summary = {}

    model_name_base = os.path.basename(model_name)

    for config_path in tqdm(json_configs, desc="Task config files"):
        task_list = load_json_config(config_path)

        for task in tqdm(task_list, desc="Tasks in config", leave=False):
            group = task["group"]
            task_name = task["task"]
            evaluation = task["evaluation"]
            files = task["files"]

            task_correct = task_total = 0

            for file_path in tqdm(files, desc=f"Files for {task_name}", leave=False):
                with open(file_path, encoding='utf-8') as f:
                    reader = list(csv.DictReader(f))
                    total_rows = len(reader)

                    if total_rows <= max_eval:
                        selected_rows = reader
                    else:
                        step = total_rows / max_eval
                        indices = [int(i * step) for i in range(max_eval)]
                        selected_rows = [reader[i] for i in indices]

                    questions = [row["input"] for row in selected_rows]
                    labels = [row.get("answer", "").strip() for row in selected_rows]
                    original_rows = selected_rows

                preds = call_model_batch(
                    model_obj=model_obj,
                    inputs=questions,
                    provider=provider,
                    model=model_name,
                    temperature=sampling["temperature"],
                    max_tokens=sampling["max_tokens"],
                    top_p=sampling.get("top_p", 1.0),
                    top_k=sampling.get("top_k", -1),
                    system_prompt=system_prompt
                )

                file_correct = file_total = 0
                output_rows = []
                for row, q, pred, label in tqdm(
                        zip(original_rows, questions, preds, labels),
                        total=len(questions),
                        desc=f"Evaluating {os.path.basename(file_path)}",
                        leave=False
                ):
                    variation = row.get("variation") if "variation" in row else None
                    if variation is not None:
                        result = evaluate_sample(evaluation, q, pred, label, variation)
                    else:
                        result = evaluate_sample(evaluation, q, pred, label)
                    if result is None:
                        correct_flag = ""
                    else:
                        file_total += 1
                        task_total += 1
                        correct_flag = int(bool(result))
                        if correct_flag:
                            file_correct += 1
                            task_correct += 1
                    row = dict(row)
                    row["pred"] = pred
                    row["correct"] = correct_flag
                    output_rows.append(row)

                acc = file_correct / file_total if file_total else 0
                results.append({
                    "model": model_name_base,
                    "group": group,
                    "task": task_name,
                    "file": os.path.basename(file_path),
                    "accuracy": acc,
                    "total": file_total,
                    "correct": file_correct
                })
                print(f"[{model_name_base}/{group}/{task_name}] {file_path} Accuracy: {acc:.2%}")

                output_dir = os.path.join("output", model_name_base, group, task_name)
                os.makedirs(output_dir, exist_ok=True)
                output_file_path = os.path.join(output_dir, os.path.basename(file_path))
                with open(output_file_path, 'w', encoding='utf-8', newline='') as out_f:
                    writer = csv.DictWriter(out_f, fieldnames=output_rows[0].keys())
                    writer.writeheader()
                    writer.writerows(output_rows)

            task_key = f"{model_name_base}/{group}/{task_name}"
            task_summary[task_key] = {
                "accuracy": task_correct / task_total if task_total else 0,
                "correct": task_correct,
                "total": task_total
            }

    print("\n=== Task Summary ===")
    for task_key, stats in task_summary.items():
        print(f"{task_key}: Accuracy = {stats['accuracy']:.2%} ({stats['correct']}/{stats['total']})")

    if output_csv is None:
        output_csv = f"eval_summary_{model_name_base}.csv"
    df = pd.DataFrame(results)
    df.to_csv(output_csv, index=False)
    print(f"\nDetailed evaluation saved to {output_csv}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default=None, help="Path to a specific YAML config file")
    parser.add_argument("--max_eval", type=int, default=1500, help="Maximum number of rows to evaluate per file")
    args = parser.parse_args()

    data_files = [
        "data/final_token_structure.json",
        "data/final_token_awareness.json"
    ]

    if args.config:
        yaml_files = [args.config]
    else:
        yaml_dir = "yamls"
        yaml_files = [
            os.path.join(yaml_dir, f)
            for f in os.listdir(yaml_dir)
            if f.endswith(".yaml") or f.endswith(".yml")
        ]

    for yaml_config_path in yaml_files:
        print(f"Evaluating with config: {yaml_config_path}")
        evaluate_all(
            data_files,
            yaml_config_path=yaml_config_path,
            max_eval=args.max_eval
        )
