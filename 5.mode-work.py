# 5.mode-work.py
from transformers import Trainer, TrainingArguments, DataCollatorForLanguageModeling, GPT2Config, GPT2LMHeadModel, PreTrainedTokenizerFast
from datasets import load_from_disk
import torch
import os

# --- 設置部分：載入 tokenizer (使用 transformers wrapper)，定義模型配置，初始化模型 ---

# 載入之前訓練好的 tokenizer 檔案，使用 transformers 的封裝類別
tokenizer_file_path = "tokenizer.json"
try:
    tokenizer = PreTrainedTokenizerFast(tokenizer_file=tokenizer_file_path)
    tokenizer.bos_token = "<s>"
    tokenizer.eos_token = "</s>"
    tokenizer.pad_token = "<pad>"
    tokenizer.unk_token = "<unk>"
    tokenizer.add_special_tokens({"additional_special_tokens": ["[問]", "[答]", "使用者：", "AI：", "\n"]})

    print(f"Tokenizer (transformers wrapper) 載入成功：{tokenizer_file_path}")
    print(f"載入的 Tokenizer 類別: {type(tokenizer)}")
    print(f"transformers tokenizer 已包含所有指定的特殊標記。")
    print(f"特殊標記 ID 設定完成 (transformers tokenizer):")
    print(f"  bos_token_id: {tokenizer.bos_token_id}")
    print(f"  eos_token_id: {tokenizer.eos_token_id}")
    print(f"  pad_token_id: {tokenizer.pad_token_id}")
    print(f"  unk_token_id: {tokenizer.unk_token_id}")
    print(f"  '[問]' ID: {tokenizer.convert_tokens_to_ids('[問]')}")
    print(f"  '[答]' ID: {tokenizer.convert_tokens_to_ids('[答]')}")
    print(f"  '使用者：' ID: {tokenizer.convert_tokens_to_ids('使用者：')}")
    print(f"  'AI：' ID: {tokenizer.convert_tokens_to_ids('AI：')}")
    print(f"  '\\n' ID: {tokenizer.convert_tokens_to_ids('\\n')}")

except Exception as e:
    print(f"錯誤：無法載入 tokenizer.json 檔案。請確認已執行 2-1-Tokenizer-BPE.py 且沒有錯誤。詳細錯誤：{e}")
    exit()

# 定義模型配置
# 使用在 3-Defining-the-Model.py 中使用的相同配置
# 如果你想使用不同的配置，請確保它們與你的模型架構相符
try:
    # 這裡我們假設模型是從頭開始初始化，如果已經有預訓練模型，則會載入
    # 嘗試從 'chat-model/checkpoint-5000' 載入配置，如果失敗則手動創建
    model_config_path = "./chat-model/checkpoint-5000"
    if os.path.exists(model_config_path):
        config = GPT2Config.from_pretrained(model_config_path)
        print(f"配置從 '{model_config_path}' 載入成功。")
    else:
        # 由於你之前的輸出顯示模型未找到檢查點，所以我們手動創建配置
        # 確保 vocab_size 與 tokenizer 的詞彙表大小一致
        # n_embd, n_layer, n_head 這些參數應該與你在 3-Defining-the-Model.py 中定義的保持一致
        config = GPT2Config(
            vocab_size=tokenizer.vocab_size,  # 使用 tokenizer 的詞彙表大小
            n_embd=128,  # 請確保這個值與 3-Defining-the-Model.py 中的 n_embd 相同
            n_layer=12,  # 請確保這個值與 3-Defining-the-Model.py 中的 n_layer 相同
            n_head=8,    # 請確保這個值與 3-Defining-the-Model.py 中的 n_head 相同
            # 其他 GPT2Config 參數如果需要可以手動設定
        )
        print(f"無法從 '{model_config_path}' 載入配置，將使用預設或手動配置: {model_config_path} is not a local folder and is not a valid model identifier listed on 'https://huggingface.co/models'")
        print(f"模型配置已手動創建：vocab_size={config.vocab_size}, n_embd={config.n_embd}, n_layer={config.n_layer}, n_head={config.n_head}")


    # 初始化模型
    # 如果要從檢查點恢復訓練，請使用 GPT2LMHeadModel.from_pretrained(model_directory)
    # 如果是從頭開始訓練，則使用 GPT2LMHeadModel(config)
    # 根據你的輸出，看起來是從頭開始初始化模型
    # 檢查是否已存在訓練好的模型，如果存在則載入，否則從頭初始化
    model_directory = "./chat-model/checkpoint-5000" # 假設這是你最後保存模型的地方
    if os.path.exists(model_directory) and os.path.isdir(model_directory):
        model = GPT2LMHeadModel.from_pretrained(model_directory)
        print(f"模型從 '{model_directory}' 載入成功。")
    else:
        model = GPT2LMHeadModel(config)
        print("未找到檢查點模型，將從頭開始初始化模型。")


    print("模型初始化完成。")

except Exception as e:
    print(f"模型初始化錯誤：{e}")
    exit()

# 載入 tokenized dataset (由 2-2-Tokenization-dataset.py 生成)

tokenized_dataset = load_from_disk("tokenized_dataset")
print(f"Tokenized dataset 載入成功，共 {len(tokenized_dataset)} 筆資料。")
print(f"Tokenized dataset 欄位: {tokenized_dataset.column_names}")

# 檢查樣本
for i in range(min(5, len(tokenized_dataset))):
    sample = tokenized_dataset[i]
    print(f"Sample {i}:")
    print(f"  input_ids length: {len(sample['input_ids'])}")
    print(f"  labels length: {len(sample['labels'])}")
    print(f"  labels type: {type(sample['labels'])}")

data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False
)
print("Data Collator 定義完成。")

# 設定訓練參數
training_args = TrainingArguments(
    output_dir="./chat-model", # 模型和檢查點的保存目錄
    overwrite_output_dir=True, # 如果輸出目錄已存在，是否覆蓋
    num_train_epochs=10, # 訓練的輪數 (Epochs)
    per_device_train_batch_size=8, # 每個裝置的訓練批次大小
    gradient_accumulation_steps=2, # 梯度累積步數，用於模擬更大的批次大小 (batch_size * gradient_accumulation_steps)
    learning_rate=5e-5, # 學習率，可以調整
    weight_decay=0.01, # 權重衰減
    adam_beta1=0.9, # AdamW 優化器的 beta1 參數
    adam_beta2=0.999, # AdamW 優化器的 beta2 參數
    adam_epsilon=1e-8, # AdamW 優化器的 epsilon 參數
    max_grad_norm=1.0, # 梯度裁剪的閾值，防止梯度爆炸
    warmup_steps=500, # 學習率預熱步數
    logging_dir="./logs", # 日誌保存目錄
    logging_steps=10, # 每隔多少步記錄一次訓練日誌
    save_steps=500, # 每隔多少步保存一次模型檢查點
    save_total_limit=2, # 最多保存多少個檢查點
    # accelerate 會自動處理多 GPU 或 CPU 訓練，只要安裝了 accelerate 即可
    # group_by_length=True, # 如果序列長度差異較大，開啟這個選項可以提高訓練效率
    # metric_for_best_model="eval_loss", # 如果有驗證集，可以設定最佳模型的衡量指標
    # evaluation_strategy="steps", # 如果有驗證集，設定評估策略
)

# 創建 Trainer
trainer = Trainer(
    model=model, # 訓練的模型物件
    args=training_args, # 訓練參數
    train_dataset=tokenized_dataset, # 訓練資料集
    data_collator=data_collator, # 資料整理器
)

print("Trainer 定義完成。")

# 開始訓練
print("開始訓練...")
try:
    # 檢查是否可以使用 CUDA (GPU)
    if torch.cuda.is_available():
        print(f"發現 CUDA 裝置：{torch.cuda.get_device_name(0)}。訓練將在 GPU 上進行。")
    else:
        print("未發現 CUDA 裝置。訓練將在 CPU 上進行，這可能需要更長時間。")

    trainer.train()
    print("訓練完成。")

    # 訓練完成後保存模型和 tokenizer
    output_dir = "./chat-model"
    os.makedirs(output_dir, exist_ok=True)
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir) # 保存 tokenizer
    print(f"模型和 tokenizer 已保存到 '{output_dir}'")

except Exception as e:
    print(f"訓練過程中發生錯誤: {e}")