# TASE Benchmark for Token-Aware & Structured Evaluation

*Official codebase accompanying the paper **“TASE: Token Awareness and Structured Evaluation for Multilingual Language Models.”***

------

## 🔍 What is TASE?

TASE is a multilingual benchmark that probes **fine-grained token perception** and **structural reasoning** in Large Language Models (LLMs).

| Category            | Tasks (sub-folders under `tasks/`)                           |
| ------------------- | ------------------------------------------------------------ |
| **Token Awareness** | `diff_tokens`, `freq_count`, `sentence_length`, `shuffle_tokens`, `sort_lengths` |
| **Token Structure** | `component_count`, `component_split`, `dot_matrix`, `structure_riddle`, `variant_normalize` |

Each task ships with

- a **synthetic data pipeline** (`tasks/`, `generate_code/`)
- ready-made **YAML configs** (all stored in **`yamls/`**)
- automatic **metrics & evaluation** scripts (`evaluate/`)

------

## 📂 Repository Layout

```
├─data/                # Pre-generated evaluation sets & example outputs
├─evaluate/            # Scoring & batch-evaluation utilities
│  ├─run_eval.py       # Evaluate one model on one YAML config
│  └─batch_eval.py     # Evaluate many models / configs in bulk
├─tasks/               # Source code & assets for each of the 10 tasks
│  ├─token_awareness/
│  └─token_structure/
└─yamls/               # ★ All YAML config files live here
```

------

## ⚡ Quick Start

1. **Set up the environment**

   ```bash
   python -m venv .venv && source .venv/bin/activate      # optional but recommended
   pip install -r requirements.txt
   ```

2. **Run a single evaluation**

   ```bash
   python evaluate/run_eval.py --config yamls/<your_config>.yaml
   ```

   The script loads the YAML from `yamls/`, runs the model, and writes results to `output/<config_name>/`.

3. **Score an existing set of model outputs**
    (useful if you already have generations in `output/`)

   ```bash
   python evaluate/batch_eval.py --input_dir output/ --output_dir output_metric/
   ```

------

## 🛠️ Configuration (YAML)

- **One YAML per experiment** (model × task × language).
- Place **all** YAML files in the **`yamls/`** directory; 

Key fields inside a YAML:

```yaml
# Inference provider type: choose from "hf" | "api" | "vllm"
provider: xxx   # e.g., "hf" (HuggingFace), "api" (remote API), "vllm" (local vLLM)

# Model name or path:
# - For provider=hf or vllm: local path or HuggingFace Hub name
# - For provider=api: API model name
model: xxxxxx

# Common generation parameters (shared across all providers; some may be ignored depending on provider)
sampling:
  temperature: 0.7         # Sampling temperature for diversity
  max_tokens: 8192         # Maximum number of tokens to generate
  top_p: 0.95              # Nucleus sampling (top-p) threshold
  top_k: 50                # Top-k sampling limit
  system_prompt: "You need to put the final result inside <answer></answer>."  # System-level prompt, if supported

# HuggingFace pipeline parameters (only used when provider=hf)
hf:
  trust_remote_code: true  # Allow loading custom code from remote repositories

# vLLM-specific parameters (only used when provider=vllm)
vllm:
  max_model_len: 10000     # Maximum context length supported by the model (default is 10000)

# API-specific parameters (only used when provider=api)
api:
  base_url: https://your-api-base-url.com/v1  # API endpoint URL
  api_key: your-api-key                       # API key (keep secure)
  threads: 50                                  # Number of concurrent threads

```

## 🏗️ Dataset-Generation Pipeline

If you wish to **rebuild the benchmark from scratch**, go to any task’s
 `generate_code/` directory and simply run *each* Python script you find there.
 Scripts are usually named to reflect their stage—e.g.:

```
tasks/token_structure/component_split/generate_code/
  ├─en.py
  ├─zh.py
  └─kor.py
```

Run them in the natural numeric / lexical order (or the order noted in comments) and the fresh dataset will appear under the corresponding `dataset/` folder. Repeat for every task whose data you want to regenerate.
