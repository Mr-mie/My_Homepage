from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import requests

load_dotenv()

app = Flask(__name__)
CORS(app)

API_URL = os.environ.get("DASHSCOPE_API_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions")
API_KEY = os.environ.get("DASHSCOPE_API_KEY", "")

SYSTEM_PROMPT = """你是艾斯卡诺的数字分身，访客可以通过你和艾斯卡诺交流。

=== 我只提供以下确定信息，其他都是不知道或不存在 ===

关于我：
- 名字：艾斯卡诺
- 职业：系统测试工程师
- 一句话介绍：正在努力学习AI的小白
- 正在做：搭自己的个人主页，整理作品集
- 擅长方向：AI应用、知识整理
- 兴趣：打游戏、健身、AI应用
- 特点：喜欢把复杂问题简单化

作品集：
1. 个人主页 - 使用HTML/CSS/JavaScript搭建的个人展示页面，集成数字分身聊天功能
2. AI数字分身 - 基于大语言模型的智能聊天机器人，可模拟个人身份进行对话
3. 知识整理系统 - 个人知识库管理工具，支持知识分类、标签管理和快速检索

联系方式：
- 邮箱：1943311505@qq.com

=== 绝对规则（不能违反） ===
1. 只说我上面列出的内容，不要扩展
2. 没提到的细节，一律说"不知道"或"这个没提供"
3. 没上传GitHub就说没上传，没做过的就说没做过
4. 不要用"可能""大概""也许"这类猜测词汇
5. 如果一个问题涉及我没提供的信息，直接说"这个我不清楚，建议发邮件问我"

=== 说话方式 ===
- 简洁：一句话说清楚
- 真诚：不知道就说不知道
- 像朋友聊天，不要像写报告

记住：你是我的分身，我没说过的，你就不知道。"""

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '')
        conversation_history = data.get('history', [])

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        for msg in conversation_history:
            messages.append(msg)
        
        messages.append({"role": "user", "content": user_message})

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "qwen-plus",
            "messages": messages,
            "max_tokens": 500,
            "temperature": 0.7
        }

        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            ai_reply = result['choices'][0]['message']['content']
            return jsonify({"success": True, "reply": ai_reply})
        else:
            return jsonify({
                "success": False, 
                "error": f"API error: {response.status_code}",
                "reply": "抱歉，我暂时遇到了一些问题，请稍后再试。"
            })

    except requests.exceptions.Timeout:
        return jsonify({"success": False, "error": "timeout", "reply": "抱歉，响应超时了，请再试一次。"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e), "reply": "抱歉，出了点问题，请稍后再试。"})

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    print("=" * 50)
    print("艾斯卡诺的数字分身后端服务")
    print("=" * 50)
    print("服务地址: http://localhost:5000")
    print("API 端点: http://localhost:5000/api/chat")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)
