import time
from typing import List, Union
from transformers.pipelines import TextGenerationPipeline
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm  

def call_model_batch(
    model_obj: Union[TextGenerationPipeline, OpenAI],
    inputs: List[str],
    provider: str,
    model: str,
    temperature: float = 0.7,
    max_tokens: int = 4096,
    top_p: float = 1.0,
    top_k: int = -1,
    system_prompt: str = "You are a helpful assistant.",
    threads: int = 20  
) -> List[str]:
    results = [None] * len(inputs)

    if provider == "hf":
        for idx, prompt in enumerate(tqdm(inputs, desc="Generating (hf)")):
            try:
                output = model_obj(prompt, max_new_tokens=max_tokens, temperature=temperature)[0]["generated_text"]
            except Exception as e:
                output = f"<error>{str(e)}</error>"
            results[idx] = output

    elif provider == "api":
        def process(idx, prompt):
            try:
                response = model_obj.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return idx, response.choices[0].message.content
            except Exception as e:
                return idx, f"<error>{str(e)}</error>"

        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [executor.submit(process, idx, prompt) for idx, prompt in enumerate(inputs)]
            for future in tqdm(as_completed(futures), total=len(futures), desc="Generating (api)"):
                idx, result = future.result()
                results[idx] = result
    
    elif provider == "vllm":
        from vllm import SamplingParams
        sampling_params = SamplingParams(
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            top_k=top_k if top_k > 0 else None,
        )
        
        conversations = [
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
            for prompt in inputs
        ]
        outputs = model_obj.chat(
            messages=conversations,
            sampling_params=sampling_params,
            use_tqdm=True,
        )
        for idx, output in enumerate(outputs):
            results[idx] = output.outputs[0].text.strip() if output.outputs else "<error>Empty output</error>"

    else:
        raise ValueError(f"Unsupported provider: {provider}")


    return results
