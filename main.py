from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import requests
import re
import os

app = FastAPI()

# 静态文件挂载（网页目录）
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def get_index():
    return FileResponse("static/index.html")

class NicknameInput(BaseModel):
    nickname: str

def extract_mbti(text):
    match = re.search(r"\b(INFP|ENFP|INFJ|ENFJ|INTP|ENTP|INTJ|ENTJ|ISFP|ESFP|ISTP|ESTP|ISFJ|ESFJ|ISTJ|ESTJ)\b", text)
    return match.group(1) if match else "未知"

api_key = os.getenv("DEEPSEEK_API_KEY", "")
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

@app.post("/predict")
def predict_mbti(input: NicknameInput):
    nickname = input.nickname

    messages = [
        {"role": "system", "content": "你是人格心理学专家，请根据用户昵称预测其 MBTI 类型。只返回最可能的一个类型，无需解释。"},
        {"role": "user", "content": "昵称：炸毛超超"}, {"role": "assistant", "content": "ENFJ"},
        {"role": "user", "content": "昵称：小熊不吃肉"}, {"role": "assistant", "content": "INFP"},
        {"role": "user", "content": "昵称：冷静分析机器"}, {"role": "assistant", "content": "INTP"},
        {"role": "user", "content": "昵称：执行总监K"}, {"role": "assistant", "content": "ESTJ"},
        {"role": "user", "content": "昵称：浪漫冒险人"}, {"role": "assistant", "content": "ENFP"},
        {"role": "user", "content": "昵称：安静观察员"}, {"role": "assistant", "content": "ISTP"},
        {"role": "user", "content": "昵称：白日梦想家"}, {"role": "assistant", "content": "ISFP"},
        {"role": "user", "content": "昵称：世界尽头C"}, {"role": "assistant", "content": "INFJ"},
        {"role": "user", "content": "昵称：蓝图规划员"}, {"role": "assistant", "content": "INTJ"},
        {"role": "user", "content": "昵称：星际领导官"}, {"role": "assistant", "content": "ENTJ"},
        {"role": "user", "content": "昵称：欢乐小旋风"}, {"role": "assistant", "content": "ESFP"},
        {"role": "user", "content": "昵称：完美事务机"}, {"role": "assistant", "content": "ISTJ"},
        {"role": "user", "content": "昵称：猫系热心肠"}, {"role": "assistant", "content": "ISFJ"},
        {"role": "user", "content": "昵称：谈判艺术家"}, {"role": "assistant", "content": "ENTP"},
        {"role": "user", "content": "昵称：暖阳女孩"}, {"role": "assistant", "content": "ESFJ"},
        {"role": "user", "content": f"昵称：{nickname}"}
    ]

    payload = {
        "model": "deepseek-chat",
        "messages": messages
    }

    try:
        response = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=payload, timeout=10)
        result = response.json()["choices"][0]["message"]["content"]
        mbti = extract_mbti(result)
    except Exception as e:
        return {"mbti": "未知", "error": str(e)}

    return {"mbti": mbti}
