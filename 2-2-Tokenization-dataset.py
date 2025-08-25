from datasets import load_dataset, Dataset
from transformers import PreTrainedTokenizerFast
import os

tokenizer_path = "tokenizer.json"
tokenizer = PreTrainedTokenizerFast(tokenizer_file=tokenizer_path)
tokenizer.bos_token = "<s>"
tokenizer.eos_token = "</s>"
tokenizer.pad_token = "<pad>"
tokenizer.unk_token = "<unk>"
tokenizer.add_special_tokens({"additional_special_tokens": ["使用者：", "AI：", "\n"]})
print("Tokenizer (transformers wrapper) 載入成功。")

dataset = load_dataset("json", data_files="train.jsonl", split="train")
print(f"資料集載入成功，共 {len(dataset)} 筆資料。")

def tokenize_function(examples):
    tokenized_output = tokenizer(
        examples['text'],
        truncation=True,         # 啟用截斷
        padding='max_length',    # 啟用填充至最大長度
        max_length=512,          # 設定最大序列長度
        return_attention_mask=True,
        return_token_type_ids=False
    )
    # 複製 input_ids 作為 labels
    labels = tokenized_output["input_ids"].copy()
    
    # 檢查 labels 的結構，確保是 list of lists of integers
    if not isinstance(labels, list):
        raise ValueError(f"labels 不是 list 類型，得到 {type(labels)}")
    for i, label in enumerate(labels):
        if not isinstance(label, list):
            raise ValueError(f"labels[{i}] 不是 list 類型，得到 {type(label)}")
        if not all(isinstance(x, int) for x in label):
            raise ValueError(f"labels[{i}] 包含非整數值")
    
    tokenized_output["labels"] = labels
    return tokenized_output

print("開始 tokenization 數據集...")
tokenized_dataset = dataset.map(
    tokenize_function,
    batched=True,
    remove_columns=dataset.column_names
)
print("Tokenization 完成。")
print(f"Tokenized dataset 結構: {tokenized_dataset}")
print(f"Tokenized dataset 範例 (第一筆資料): {tokenized_dataset[0]}")

output_dataset_path = "./tokenized_dataset"
tokenized_dataset.save_to_disk(output_dataset_path)
print(f"Tokenized dataset 已保存到 '{output_dataset_path}'。")