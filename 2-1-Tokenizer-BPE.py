from tokenizers import Tokenizer, models, trainers, pre_tokenizers

tokenizer = Tokenizer(models.BPE())
tokenizer.pre_tokenizer = pre_tokenizers.Whitespace()

# 添加你定義的特殊標記
# 移除 [問] 和 [答]，只保留對話中實際會出現的標記
special_tokens = ["<pad>", "<s>", "</s>", "<unk>", "使用者：", "AI：", "\n"] # 換行符也可能需要作為特殊token處理

trainer = trainers.BpeTrainer(
    vocab_size=30000, # 詞彙表大小，可以根據數據量調整
    min_frequency=2,  # 詞元最小出現頻率
    special_tokens=special_tokens
)

files = ["train.txt"]  # 確保 train.txt 已經包含了新格式的數據
tokenizer.train(files, trainer)
tokenizer.save("tokenizer.json")
print("Tokenizer 訓練並保存完成。")

# 建議驗證一下特殊標記是否被正確添加到詞彙表中
loaded_tokenizer = Tokenizer.from_file("tokenizer.json")
print(f"Tokenizer 詞彙表大小: {loaded_tokenizer.get_vocab_size()}")
for token in special_tokens:
    print(f"'{token}' ID: {loaded_tokenizer.token_to_id(token)}")