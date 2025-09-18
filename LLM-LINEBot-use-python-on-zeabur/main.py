import os
from dotenv import load_dotenv
import io
import requests
from llm import ChatGPT
from flask import Flask, request, abort, send_from_directory
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageMessage, ImageSendMessage, QuickReply, QuickReplyButton, MessageAction

import warnings
from linebot import LineBotSdkDeprecatedIn30

env_path = os.path.join(os.path.dirname(__file__), "api.env")
# 載入 .env 檔(openi_api_key.env)
load_dotenv(env_path)


line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
web_handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))
working_status = os.getenv("DEFALUT_TALKING", default="true").lower() == "true"

app = Flask(__name__)
chatgpt = ChatGPT()

# domain root
@app.route('/')
def home():
    return '<h1>This is AI TA web</h1>'

# Listen for all Post Requests from /callback
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    print(body)
    
    app.logger.info("Request body: " + body)
    try:
        web_handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

def start_loading_animation(chat_id, loading_seconds):
    url = "https://api.line.me/v2/bot/chat/loading/start"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('LINE_CHANNEL_ACCESS_TOKEN')}"
    }
    data = {
        "chatId": chat_id,
        "loadingSeconds": loading_seconds
    }
    response = requests.post(url, headers=headers, json=data)
    return response.status_code

@web_handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    """LINE MessageAPI message processing"""
    if event.source.user_id == 'Udeadbeefdeadbeefdeadbeefdeadbeef':
        return 'OK'
    
    global working_status

    if event.message.type != "text":
        return

    if event.message.text[:3] == "啟動":
        working_status = True
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="啟動AI"))
        return

    if event.message.text[:5] == "關閉AI":
        working_status = False
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='AI下班去，喚醒請輸入"啟動"'))
        return

    if working_status:
        start_loading_animation(event.source.user_id, 5)
        chatgpt.add_msg(f"HUMAN:{event.message.text}?\n")
        reply_msg = chatgpt.get_response().replace("AI:", "", 1)
        chatgpt.add_msg(f"AI:{reply_msg}\n")
        
        questions = ["了解更多", "出2個練習題", "相關觀念", "關閉AI"]
        # 將追問問題設為 Quick Replies
        quick_reply_buttons = [
            QuickReplyButton(action=MessageAction(label=question, text=question))
            for question in questions
        ]
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text=f"助教:{reply_msg}", 
                quick_reply=QuickReply(items=quick_reply_buttons)
            )
        )

@web_handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    # 處理圖片訊息
    message_id = event.message.id

    image_content = line_bot_api.get_message_content(event.message.id)
    # path = chatgpt.get_user_image(image_content)
    # link = chatgpt.upload_img_link(path)

    # # 調用OpenAI API進行圖片處理
    # response = chatgpt.process_image_link(link)
    
    # 假設OpenAI回傳的結果包含在response['choices'][0]['text']
    # reply_msg = response['choices'][0]['text']
    # line_bot_api.reply_message(
    #     event.reply_token,
    #     TextSendMessage(text=f"助教:{reply_msg}"))
    image_path = os.path.join('images', f'{message_id}.jpg')

    # 將圖片內容寫入本地文件
    with open(image_path, 'wb') as f:
        for chunk in image_content.iter_content():
            f.write(chunk)

    if(image_content != None):

        # line_bot_api.reply_message(
        #     event.reply_token,
        #     TextSendMessage(text=f"助教:圖片酷喔!"))
        
        print(f'\n https://e74ad8ddf001.ngrok-free.app\{image_path} \n')

        line_bot_api.reply_message(
            event.reply_token,
            [TextSendMessage(text=f"助教:圖片酷喔!"),
            ImageSendMessage( original_content_url=f'https://e74ad8ddf001.ngrok-free.app/images/{message_id}.jpg',  # 使用公開 URL 發送圖片
                          preview_image_url=f'https://e74ad8ddf001.ngrok-free.app/images/{message_id}.jpg')])
        

@app.route('/images/<filename>')
def serve_image(filename):
    return send_from_directory('images', filename)

if __name__ == "__main__":
    warnings.filterwarnings("ignore", category=LineBotSdkDeprecatedIn30)
    app.run(debug=True)
