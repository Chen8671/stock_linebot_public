import os
import sys
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *

app = Flask(__name__)

# 從環境變數讀取 LINE 設定
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_secret is None:
    print('請設定 LINE_CHANNEL_SECRET 環境變數')
    sys.exit(1)
if channel_access_token is None:
    print('請設定 LINE_CHANNEL_ACCESS_TOKEN 環境變數')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

@app.route("/callback", methods=['POST'])
def callback():
    # 取得 X-Line-Signature 標頭內容
    signature = request.headers.get('X-Line-Signature', '')
    # 取得 request body 並轉為文字
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # 處理 webhook 傳來的訊息
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 以下是一個示範：收到文字訊息時回覆圖文選單
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text.strip().lower()
    if text == 'menu' or text == '選單':
        # 使用 CarouselTemplate 建立多區塊的圖文選單
        flex_message = TemplateSendMessage(
            alt_text='選單',
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
                        thumbnail_image_url='https://example.com/stock.png',
                        title='股票 Stock',
                        text='查看股票價格',
                        actions=[
                            URIAction(label='查看', uri='https://yourwebsite.com/stock')
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url='https://example.com/finance-tips.png',
                        title='理財技巧 Finance tips',
                        text='獲取理財建議',
                        actions=[
                            URIAction(label='獲取', uri='https://yourwebsite.com/finance-tips')
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url='https://example.com/rate-inquiry.png',
                        title='匯率查詢 Rate inquiry',
                        text='查詢今日匯率',
                        actions=[
                            URIAction(label='查詢', uri='https://yourwebsite.com/rate-inquiry')
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url='https://example.com/stock-checkup.png',
                        title='股票健康檢查 Stock checkup',
                        text='查看股票健康狀況',
                        actions=[
                            URIAction(label='檢查', uri='https://yourwebsite.com/stock-checkup')
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url='https://example.com/video.png',
                        title='影片 Video',
                        text='觀看金融相關影片',
                        actions=[
                            URIAction(label='觀看', uri='https://yourwebsite.com/video')
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url='https://example.com/finance-website.png',
                        title='理財網站 Finance website',
                        text='訪問理財網站',
                        actions=[
                            URIAction(label='訪問', uri='https://yourwebsite.com/finance-website')
                        ]
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, flex_message)
    else:
        # 若不符合觸發條件，回覆預設訊息
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="請輸入 'menu' 或 '選單' 來查看功能選單。")
        )

if __name__ == "__main__":
    # Render 會動態設定 PORT，預設 5000 當作備用
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
