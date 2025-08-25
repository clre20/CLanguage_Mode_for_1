import glob
import os

# 確保 train.txt 包含來自 ptt_dialogues.txt 的內容
# ptt_dialogues.txt 應該包含完整的對話序列，每條一行
input_file = os.path.join("data", "ptt_dialogues.txt") # 使用 ptt_dialogues.txt

if not os.path.exists(input_file):
    print(f"錯誤: 找不到輸入檔案 '{input_file}'。請確認已執行 1-1-ptt_crawler.py。")
    exit()

with open("train.txt", "w", encoding="utf-8") as outfile:
    with open(input_file, "r", encoding="utf-8") as infile:
        for line in infile:
            stripped_line = line.strip()
            if stripped_line: # 只寫入非空行
                outfile.write(stripped_line + "\n")
    # 可以選擇性地加入其他文章數據，但現在先專注於對話數據
    # for fname in glob.glob("data/*.txt"):
    #     if os.path.basename(fname) != "ptt_dialogues.txt":
    #         with open(fname, encoding="utf-8") as infile:
    #             outfile.write(infile.read() + "\n")

print(f"已將 '{input_file}' 內容合併到 'train.txt'。")