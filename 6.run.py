from transformers import pipeline
import os

# 指定訓練好的模型和 tokenizer 儲存的目錄
# 將這裡修改為指向你的最新檢查點目錄
model_directory = "./chat-model/checkpoint-4500" # 或者 "./chat-model/checkpoint-4500" 如果那是你想要的最新一個

# 檢查模型目錄是否存在
if not os.path.exists(model_directory):
    print(f"錯誤: 找不到模型目錄 '{model_directory}'。請確認 5.mode-work.py 已成功運行並保存模型到此目錄。")
    exit()

# 使用 transformers 的 pipeline 功能載入訓練好的模型和 tokenizer
# pipeline 會自動識別目錄中的模型和 tokenizer 檔案
try:
    print(f"正在從 '{model_directory}' 載入模型和 tokenizer...")
    # 指定任務為 "text-generation" (文字生成)
    generator = pipeline("text-generation", model=model_directory, tokenizer=model_directory)
    print("模型和 tokenizer 載入完成。")

except Exception as e:
    print(f"錯誤: 無法載入模型或 tokenizer 從 '{model_directory}'。詳細錯誤: {e}")
    exit()


# 定義你的輸入 Prompt
input_prompt = "<s>使用者：台南最近發生什麼是？\nAI："

print(f"\n輸入 Prompt: {input_prompt}")
try:
    # 生成文字
    generated_output = generator(
        input_prompt,
        max_length=150, # 生成文本的最大長度
        num_return_sequences=1, # 生成 1 個結果
        # 以下參數可以根據需要調整，用於控制生成品質
        do_sample=True,
        top_k=50,
        top_p=0.95,
        temperature=0.7,
        pad_token_id=generator.tokenizer.pad_token_id # 確保有設定 pad_token_id
    )

    # 打印生成的文本
    for i, output in enumerate(generated_output):
        # 移除非文本內容，只保留 AI 的回答部分
        # 找到 "AI：" 之後的部分，並移除 "</s>"
        generated_text = output['generated_text']
        ai_start_index = generated_text.find("AI：")
        if ai_start_index != -1:
            # 從 "AI：" 後面開始取，並移除可能的 </s> 標記
            response = generated_text[ai_start_index + len("AI："):].replace("</s>", "").strip()
            print(f"生成的回應 {i+1}: {response}")
        else:
            print(f"生成的回應 {i+1}: {generated_text.replace('</s>', '').strip()}")


except Exception as e:
    print(f"生成文字時發生錯誤: {e}")