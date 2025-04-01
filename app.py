import os
import sys
import yfinance as yf
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *

app = Flask(__name__)

# 直接硬編碼 LINE Channel 的設定資訊
channel_secret = "bP4+qoMkxVBTp/frpIaE4G1u4mvsPXWgyNIUJuIwdBqP8wHwZHTdEG64EYzgu0boK6ru/zS2n6ACBPp7XIUxlxSUHDrDfZmT2fQRHXhiLnonhByqaPilVH5ejhV2647pAZDg75xeH0mVIbN4Tkd6dQdB04t89/1O/w1cDnyilFU="
channel_access_token = "7bf4becaf162f5e885ab92d0afa53630"

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

@app.route("/callback", methods=['POST'])
def callback():
    # 取得 X-Line-Signature 標頭內容
    signature = request.headers.get('X-Line-Signature', '')
    # 取得 request body 並轉為純文字
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text.strip()
    lower_text = text.lower()

    # 使用者輸入 "menu" 或 "選單" 時，回傳圖文選單
    if lower_text == 'menu' or lower_text == '選單':
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

    # 使用者輸入 "報價 股票代碼" 或 "查股 股票代碼" 時，使用 yfinance 取得股票資料
    elif lower_text.startswith('報價') or lower_text.startswith('查股'):
        parts = text.split()
        if len(parts) >= 2:
            ticker = parts[1].upper()  # 股票代碼通常為大寫
        else:
            line_bot_api.reply_message(
                event.reply_token, 
                TextSendMessage(text="請輸入正確格式，例如：報價 2330")
            )
            return
        try:
            stock = yf.Ticker(ticker)
            stock_info = stock.info
            current_price = stock_info.get('regularMarketPrice', 'N/A')
            previous_close = stock_info.get('previousClose', 'N/A')
            market_cap = stock_info.get('marketCap', 'N/A')
            reply_text = (
                f"股票代碼: {ticker}\n"
                f"現價: {current_price}\n"
                f"前收價: {previous_close}\n"
                f"市值: {market_cap}"
            )
        except Exception as e:
            reply_text = f"無法取得 {ticker} 的資料，請確認代碼是否正確。"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text)
        )
    else:
        # 其他消息回覆提示訊息
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="請輸入 'menu' 或 '選單' 來查看功能選單，或輸入 '報價 股票代碼' / '查股 股票代碼' 來查詢股票資訊。")
        )

if __name__ == "__main__":
    # Render 部署時會以環境變數 PORT 指定埠號，若無則預設 5000
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
