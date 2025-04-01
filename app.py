import os
import requests  # 用於發送 HTTP 請求
import re        # 匯入正則表達式模組
import yfinance  # 匯入股票模組，用於處理股票相關功能

from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import ImageSendMessage, TextSendMessage

# 初始化 Flask 應用程式
app = Flask(__name__)

# 設定 LINE Bot 的 Channel Access Token 和 Channel Secret
line_bot_api = LineBotApi(os.getenv('bP4+qoMkxVBTp/frpIaE4G1u4mvsPXWgyNIUJuIwdBqP8wHwZHTdEG64EYzgu0boK6ru/zS2n6ACBPp7XIUxlxSUHDrDfZmT2fQRHXhiLnonhByqaPilVH5ejhV2647pAZDg75xeH0mVIbN4Tkd6dQdB04t89/1O/w1cDnyilFU='))  # 替換成你的 Channel Access Token
handler = WebhookHandler(os.getenv('7bf4becaf162f5e885ab92d0afa53630'))         # 替換成你的 Channel Secret

# 模擬問卷類型的圖片對象（需自定義）
class Questionnaire:
    type_A = "https://example.com/image_A.jpg"  
    type_B = "https://example.com/image_B.jpg"
    type_C = "https://example.com/image_C.jpg"
    type_D = "https://example.com/image_D.jpg"
    type_E = "https://example.com/image_E.jpg"
    type_F = "https://example.com/image_F.jpg"
    type_G = "https://example.com/image_G.jpg"

questionnaire = Questionnaire()

# 處理使用者訊息的主要邏輯
@app.route("/callback", methods=['POST'])
def callback():
    # 獲取 LINE 平台發送的請求資料與簽名
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        # 處理 LINE 事件
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)  # 若簽名驗證失敗則返回 400

    return 'OK'

# 處理訊息事件
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text  # 使用者的文字訊息
    uid = event.source.user_id  # 使用者 ID

    # 使用字典管理類型對應的圖片 URL
    image_mapping = {
        "類型A": questionnaire.type_A,
        "類型B": questionnaire.type_B,
        "類型C": questionnaire.type_C,
        "類型D": questionnaire.type_D,
        "類型E": questionnaire.type_E,
        "類型F": questionnaire.type_F,
        "類型G": questionnaire.type_G
    }

    if msg in image_mapping:
        img_url = image_mapping[msg]
        line_bot_api.push_message(uid, ImageSendMessage(
            original_content_url=img_url,
            preview_image_url=img_url
        ))
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="無法辨識的類型，請再次檢查！"))
