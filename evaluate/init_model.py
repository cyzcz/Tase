

from typing import Optional, Dict, Any, Union
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from openai import OpenAI


def init_model(
    provider: str,
    model: str,
    options: Optional[Dict[str, Any]] = None,
) -> Union[pipeline, OpenAI]:
    options = options or {}

    if provider == "hf":
        tokenizer = AutoTokenizer.from_pretrained(model)
        model_obj = AutoModelForCausalLM.from_pretrained(model, device_map="auto")
        return pipeline("text-generation", model=model_obj, tokenizer=tokenizer)

    elif provider == "api":
        api_key = options["api_key"]
        base_url = options["base_url"]
        return OpenAI(api_key=api_key, base_url=base_url, timeout=300)

    elif provider == "vllm":
        try:
            from vllm import LLM 
        except ImportError:
            raise ImportError("vllm: pip install vllm")

        import torch

        
        num_gpus = torch.cuda.device_count()
        if num_gpus == 0:
            raise RuntimeError("未检测到可用的 GPU，请检查环境！")
        
        max_model_len = options.get("max_model_len", 10000)

        
        llm = LLM(
            model=model,
            tensor_parallel_size=num_gpus,
            max_model_len=max_model_len,
            device="cuda",
        )
        return llm

    else:
        raise ValueError(f"Unsupported provider: {provider}")
