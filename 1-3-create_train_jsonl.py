# 1-3-create_train_jsonl.py
import json
import os

def create_jsonl_from_txt_for_dialogues(input_txt_file, output_jsonl_file):
    """
    Reads a text file where each line is a complete dialogue sequence (e.g., "<s>User: ...AI: ...</s>")
    and creates a JSON Lines file where each line is {"text": "dialogue_sequence"}.

    Args:
        input_txt_file (str): Path to the input text file (e.g., train.txt).
        output_jsonl_file (str): Path to the output JSON Lines file (e.g., train.jsonl).
    """
    if not os.path.exists(input_txt_file):
        print(f"錯誤: 找不到輸入檔案 '{input_txt_file}'。請確認已執行 1-2-data.py 以生成 train.txt。")
        return

    jsonl_data = []
    with open(input_txt_file, 'r', encoding='utf-8') as f:
        for line in f:
            # 每一行都應該是一個完整的對話序列
            # 移除行尾的換行符，並檢查是否為空行
            stripped_line = line.strip()
            if stripped_line:
                jsonl_data.append({"text": stripped_line})

    if not jsonl_data:
        print(f"警告: '{input_txt_file}' 中沒有有效對話序列，'{output_jsonl_file}' 將會是空的。")
        return

    os.makedirs(os.path.dirname(output_jsonl_file) or '.', exist_ok=True) # 確保輸出目錄存在
    with open(output_jsonl_file, 'w', encoding='utf-8') as f:
        for entry in jsonl_data:
            json.dump(entry, f, ensure_ascii=False)
            f.write('\n')
    print(f"成功將 '{input_txt_file}' 轉換為 '{output_jsonl_file}'。共 {len(jsonl_data)} 條對話序列。")

if __name__ == "__main__":
    input_txt_file = "train.txt"
    output_jsonl_file = "train.jsonl"
    create_jsonl_from_txt_for_dialogues(input_txt_file, output_jsonl_file)