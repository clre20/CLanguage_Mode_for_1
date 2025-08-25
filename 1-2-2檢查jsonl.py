import json

with open("train.jsonl", "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        try:
            data = json.loads(line.strip())
            if not isinstance(data["text"], str):
                print(f"第 {i+1} 行：text 不是字串，得到 {type(data['text'])}")
        except Exception as e:
            print(f"第 {i+1} 行：格式錯誤 - {e}")