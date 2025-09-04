from vllm import LLM, SamplingParams
from transformers import AutoTokenizer
import torch
import yaml

import time
import traceback

def create_outputs(llm, tokenizer, sampling_params, prompt_file):
    with open(prompt_file, 'r', encoding='utf-8') as f:
        prompt_texts = f.read()
    prompt_texts = prompt_texts.strip().split("\n\n")
    prompts = [
        tokenizer.apply_chat_template(
            [{'role': 'user', 'content': pr}], tokenize=True,
            add_generation_prompt=True, enable_thinking=False
        ) for pr in prompt_texts
    ]
    print(len(prompt_texts), len(prompts))
    outputs = llm.generate(prompt_token_ids=prompts, sampling_params=sampling_params)
    return outputs

def main():
    try:
        with open('/src/src/configs/config.yaml', 'r') as file:
            configs = yaml.safe_load(file)
        for config in configs['experiments']:
            print(config)
            model_name = config['model']
            result_name = config['result_name']

            llm = LLM(
            model=model_name,
            max_seq_len_to_capture=4096,
            max_model_len=4096,
            dtype=torch.float16,
            seed=42,
            tensor_parallel_size=2
            )
    
            tokenizer = llm.get_tokenizer()

            sampling_params = SamplingParams(
            temperature=0.3,
            top_p=0.9,
            top_k=40,
            max_tokens=2048,
            repetition_penalty=1.0,
            seed=42
            )

            for treebank_config in config['treebanks']:
                time_res = {}
                dataset_name = treebank_config['dataset']
                prompt_start = int(treebank_config['start'])
                prompt_finish = int(treebank_config['finish'])
                assert isinstance(prompt_start, int)
                assert isinstance(prompt_finish, int)
                print(model_name, dataset_name, result_name,
                    prompt_start, prompt_finish)
                for prompt_i in range(prompt_start, prompt_finish):
                    ts = time.time()
                    outputs = create_outputs(llm, tokenizer, sampling_params, f'/src/src/prompts/{dataset_name}_prompts/prompts_2_{prompt_i}.txt')
                    t = time.time() - ts
                    time_res[(dataset_name, prompt_i)] = t
                    with open(f'/src/src/results/{result_name}_{dataset_name}_2_{prompt_i}.txt', 'w') as f:
                        for output_i in range(len(outputs)):
                            print(outputs[output_i].outputs[0].text, file=f, end="\n===========================\n")
                    print(prompt_i, len(outputs))
        
                print(dataset_name, time_res)
                with open(f'/src/src/results/{result_name}_{dataset_name}_{prompt_start}_{prompt_finish}_time.txt', 'w') as f:
                    for k, v in time_res.items():
                        print(k, v, file=f)

    except Exception as e:
        print(traceback.format_exc())
        print(e)

    time.sleep(10)
    print("FINISHED", flush=True)
    time.sleep(10)


