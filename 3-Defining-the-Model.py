from transformers import GPT2Config, GPT2LMHeadModel
from tokenizers import Tokenizer # 新增這一行，導入 Tokenizer 類別

# 載入之前訓練好的 tokenizer
# 確保 2-1-Tokenizer-BPE.py 已經成功執行並生成了 tokenizer.json 檔案
try:
    tokenizer = Tokenizer.from_file("tokenizer.json")
    print("Tokenizer 載入成功。")
except Exception as e:
    print(f"錯誤：無法載入 tokenizer.json 檔案。請確認已執行 2-1-Tokenizer-BPE.py 且沒有錯誤。詳細錯誤：{e}")
    exit()

# 調整模型配置參數
config = GPT2Config(
    vocab_size=tokenizer.get_vocab_size(),
    n_embd=128,
    n_layer=12,  # 建議值，從 64 調整為 12
    n_head=8,    # 建議值，確保 n_embd (128) 可以被 n_head (8) 整除 (128 / 8 = 16)
    # 確保設置特殊標記的 ID，這對於訓練和生成都很重要
    bos_token_id=tokenizer.token_to_id("<s>"),
    eos_token_id=tokenizer.token_to_id("</s>"),
    pad_token_id=tokenizer.token_to_id("<pad>"),
    unk_token_id=tokenizer.token_to_id("<unk>"),
)
model = GPT2LMHeadModel(config)

print(f"模型配置完成，詞彙表大小為：{config.vocab_size}")
print(f"模型參數：n_embd={config.n_embd}, n_layer={config.n_layer}, n_head={config.n_head}")

# 可以選擇將初始化的模型保存，以便在 5.mode-work.py 中載入
# 如果 5.mode-work.py 總是從頭開始訓練，則不需要在這裡保存
# model.save_pretrained("./initial_model")
# print("初始模型已保存到 ./initial_model")