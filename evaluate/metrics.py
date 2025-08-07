import re
from typing import Tuple


def extract_answer(text: str) -> str:
    if text is None:
        return ""
    match = re.search(r"<answer>(.*?)</answer>", text, re.DOTALL)
    if not match:
        match_new = re.search(r"\*\*(.*?)\*\*", text, re.DOTALL)
        if not match_new:
            return ""
        return match_new.group(1).strip() if match_new else ""
    return match.group(1).strip() if match else ""


def remove_punctuation(text: str) -> str:
    return re.sub(r"[^\w\s\u4e00-\u9fff]", "", text)

def match_answer(question: str, pred: str, label: str) -> bool:
        pred_origin=pred
        if not pred:
            return False
        pred= extract_answer(pred)
        if pred=="":
            return pred_origin==label
        if label not in ",。，:：；;、 ":
            for ch in ",。，:：；;、 ":
                pred = pred.replace(ch, "")
                label = label.replace(ch, "")
        pred = pred.lower().strip()
        label = label.lower().strip()
        return label in pred


def contains_chinese(text: str) -> bool:
    return any('\u4e00' <= ch <= '\u9fff' for ch in text)

def is_chinese(ch):
    return '\u4e00' <= ch <= '\u9fff'

def is_valid_english_word(word: str) -> bool:
    if contains_chinese(word):
        return False
    return re.fullmatch(r"[a-zA-Z]+(?:[-'][a-zA-Z]+)*", word) is not None


def is_korean(char: str) -> bool:
    return bool(re.match(r'[\uAC00-\uD7A3]', char))

def sentence_length(question: str, pred: str, label: str) -> bool:
    target_len = int(re.search(r"\d+", question).group())
    content = extract_answer(pred)
    if contains_chinese(content):
        
        return sum(1 for ch in content if '\u4e00' <= ch <= '\u9fff') == target_len
    elif any(is_korean(c) for c in content):
        
        return sum(1 for c in content if is_korean(c)) == target_len
    else:
        
        words = re.findall(r"\b[\w'-]+\b", content)
        return sum(1 for word in words if is_valid_english_word(word)) == target_len

from typing import Tuple
import re

from typing import Tuple
import re
from collections import Counter

def shuffle_tokens(question: str, pred: str, label: str) -> Tuple[bool, bool]:
    m = re.search(r"[:：]\s*([^\n\r]*)", question)
    if not m:
        return False, False
    original = m.group(1).lower().strip()
    shuffled = extract_answer(pred).lower().strip()

    def is_chinese(ch):
        return '\u4e00' <= ch <= '\u9fff'

    def is_korean(ch):
        return '\uAC00' <= ch <= '\uD7A3'

    def get_tokens(s):
        if any(is_chinese(ch) for ch in s):
            return [ch for ch in s if is_chinese(ch)]
        elif any(is_korean(ch) for ch in s):
            return [ch for ch in s if is_korean(ch)]
        else:
            
            return re.findall(r"\b[\w'-]+\b", s)

    orig_tokens = get_tokens(original)
    shuf_tokens = get_tokens(shuffled)

    tokens_match = Counter(orig_tokens) == Counter(shuf_tokens)
    if not tokens_match:
        return False, False

    
    orig_token_pos = {}
    for idx, token in enumerate(orig_tokens):
        orig_token_pos.setdefault(token, []).append(idx)

    used_pos = set()
    shuf_to_orig_pos = []
    for token in shuf_tokens:
        pos_list = orig_token_pos.get(token, [])
        for pos in pos_list:
            if pos not in used_pos:
                shuf_to_orig_pos.append(pos)
                used_pos.add(pos)
                break
        else:
            return True, False

    
    for i in range(len(shuf_to_orig_pos) - 1):
        if abs(shuf_to_orig_pos[i+1] - shuf_to_orig_pos[i]) == 1:
            return True, False

    return True, True


def split_components(question: str, pred: str, label: str) -> bool:
    pred_ans = extract_answer(pred).replace(" ", "")
    options = label.split(";")
    for opt in options:
        parts = [p.strip() for p in opt.split(",")]
        if all(part in pred_ans for part in parts):
            return True
    return False

def match_number(question:str,pred: str, label: str) -> bool:
    if not pred or not label:
        return False

    
    label_num_match = re.search(r"\d+", label)
    if not label_num_match:
        return False
    label_num = label_num_match.group()

    
    pred_content = extract_answer(pred)
    pred_numbers = re.findall(r"\d+", pred_content)
    if not pred_numbers:
        return False

    return pred_numbers[-1] == label_num

import re

def clean_text(text: str) -> str:
    symbols_to_remove = ",.。:：、；;\"'‘’“”"
    text = text.lower()
    text = text.replace("不是", "")
    text = re.sub(r"\bno\b", "", text, flags=re.IGNORECASE)
    for ch in symbols_to_remove:
        text = text.replace(ch, "")
    return text.lower().strip()

def extract_quoted(text: str) -> list:
    return re.findall(r"['\"](.*?)['\"]", text)
def tokenize(text: str) -> list:
    
    return re.findall(r'[\u4e00-\u9fa5]|[a-zA-Z]+', text)
def diff_judge(question: str,answer1: str, answer2: str, variation: str) -> bool:
    
    answer1=extract_answer(answer1)
    a1_clean = clean_text(answer1)
    a2_clean = clean_text(answer2)
    if a1_clean == a2_clean:
        return True

    
    quoted = extract_quoted(answer1)
    quoted = [clean_text(q) for q in quoted if clean_text(q)]  

    if variation.lower() in ["modify", "修改"]:
        unique_quoted = list(set(quoted))
        if len(unique_quoted) <= 2 and a2_clean in unique_quoted:
            return True
        elif len(unique_quoted) == 1 and a2_clean == unique_quoted[0]:
            return True

        tokens = tokenize(a1_clean)
        unique_tokens = list(set(tokens))
        if len(unique_tokens) == 2 and a2_clean in unique_tokens:
            return True

    return False


