import os
from flask import Flask, request, abort
import yfinance as yf
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent,
    TextMessage,
    TextSendMessage,
    TemplateSendMessage,
    CarouselTemplate,
    CarouselColumn,
    URIAction,
)

app = Flask(__name__)

# 直接硬編碼 LINE Bot 的認證資訊
line_bot_api = LineBotApi(
    'mXE1BzBQ67nBGrZGbBO0TEWrT3xy9h3rpk4sz+PGeC00bwwc3yvWz9BEANYMNpm0MqpSk7xfmEh6l2KEy/KFEAduvGPm3m7A++Sxl3eJTiSzeQlzZJhxXfDoiyEdfGnsDern1toKbzLJdDe/IvtFpwdB04t89/1O/w1cDnyilFU='
)
handler = WebhookHandler('7c7b7ddfcfa323b252f5f4d81a4bff1d')


def get_stock_info(ticker: str) -> str:
    """
    根據股票代號取得股票資訊，並組成回覆內容。
    """
    ticker = ticker.upper()
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        current_price = info.get("regularMarketPrice", "N/A")
        previous_close = info.get("previousClose", "N/A")
        market_cap = info.get("marketCap", "N/A")
        return (
            f"股票代碼：{ticker}\n"
            f"現價：{current_price}\n"
            f"前收價：{previous_close}\n"
            f"市值：{market_cap}"
        )
    except Exception as e:
        return None


@app.route("/callback", methods=["POST"])
def callback():
    # 取得 LINE 傳入的簽名與 request body
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    except Exception as e:
        print("Handler error:", e)
        abort(500)
    return "OK"


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text.strip()
    lower_text = text.lower()
    parts = text.split()

    # 1. 輸入 "menu" 或 "選單" 時，回覆圖文選單
    if lower_text in ("menu", "選單"):
        menu = TemplateSendMessage(
            alt_text="選單",
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
                        thumbnail_image_url="https://example.com/stock.png",
                        title="股票 Stock",
                        text="查看股票價格",
                        actions=[
                            URIAction(label="查看", uri="https://yourwebsite.com/stock")
                        ],
                    ),
                    CarouselColumn(
                        thumbnail_image_url="https://example.com/finance-tips.png",
                        title="理財技巧 Finance tips",
                        text="獲取理財建議",
                        actions=[
                            URIAction(label="獲取", uri="https://yourwebsite.com/finance-tips")
                        ],
                    ),
                    CarouselColumn(
                        thumbnail_image_url="https://example.com/rate-inquiry.png",
                        title="匯率查詢 Rate inquiry",
                        text="查詢今日匯率",
                        actions=[
                            URIAction(label="查詢", uri="https://yourwebsite.com/rate-inquiry")
                        ],
                    ),
                    CarouselColumn(
                        thumbnail_image_url="https://example.com/stock-checkup.png",
                        title="股票健康檢查 Stock checkup",
                        text="查看股票健康狀況",
                        actions=[
                            URIAction(label="檢查", uri="https://yourwebsite.com/stock-checkup")
                        ],
                    ),
                    CarouselColumn(
                        thumbnail_image_url="https://example.com/video.png",
                        title="影片 Video",
                        text="觀看金融相關影片",
                        actions=[
                            URIAction(label="觀看", uri="https://yourwebsite.com/video")
                        ],
                    ),
                    CarouselColumn(
                        thumbnail_image_url="https://example.com/finance-website.png",
                        title="理財網站 Finance website",
                        text="訪問理財網站",
                        actions=[
                            URIAction(label="訪問", uri="https://yourwebsite.com/finance-website")
                        ],
                    ),
                ]
            ),
        )
        line_bot_api.reply_message(event.reply_token, menu)
        return

    # 2. 輸入格式為 "報價 股票代號" 或 "查股 股票代號"
    if lower_text.startswith("報價") or lower_text.startswith("查股"):
        if len(parts) < 2:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="請輸入正確格式，例如：報價 2330"),
            )
            return

        ticker = parts[1]
        info = get_stock_info(ticker)
        if info:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=info))
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f"無法取得 {ticker.upper()} 的資料，請確認代碼是否正確。"),
            )
        return

    # 3. 直接輸入單一股票代號則直接查詢資訊
    if len(parts) == 1:
        info = get_stock_info(text)
        if info:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=info))
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f"無法取得 {text.upper()} 的資料，請確認代碼是否正確。"),
            )
        return

    # 4. 其他輸入則回覆提示訊息
    help_msg = (
        "請輸入 'menu' 或 '選單' 來查看功能選單，\n"
        "或輸入 '報價 股票代碼' / '查股 股票代碼' 來查詢股票資訊，\n"
        "也可以直接輸入股票代號，例如：2330。"
    )
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=help_msg))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
