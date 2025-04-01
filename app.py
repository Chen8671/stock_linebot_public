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

# 請確認此處的認證資訊已更新到您最新的值
line_bot_api = LineBotApi(
    'T/EUr80xzlGCYpOUBsuORZdWpWwl/EYMxZRgnyorALxmo0xp5ti+2ELOII85fYQZ1bf/tNbOy3Y2T3GFPKBrOGsJd1dkQ8t2Rhkh5Fc9SSq1Jn/+dTZljEyGzEdUfoL1n0LsPdKagWWHk5ZEyd8aygdB04t89/1O/w1cDnyilFU='
)
handler = WebhookHandler('a2180e40b0a6c2ef14fde47b59650d60')


def get_stock_info(ticker: str) -> str:
    """
    根據股票代號取得股票資訊。
    
    如果用戶輸入純數字（例如 "2330"），則自動加上 .TW 後綴查詢台灣股票資料。
    若 info 資料沒有取得正確行情數據，則嘗試利用最近 2 天的歷史資料作備援。
    """
    original = ticker.upper()
    # 如果全部為數字則自動加上 .TW
    if original.isdigit():
        ticker = original + ".TW"
    else:
        ticker = original

    print("[DEBUG] Fetching ticker:", ticker)
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        print("[DEBUG] info returned:", info)
    except Exception as e:
        print("[DEBUG] Exception while fetching info:", e)
        info = {}

    # 若 info 為空或沒有正確的行情數據，嘗試使用歷史資料
    if not info or info.get("regularMarketPrice") is None:
        try:
            hist = stock.history(period="2d")
            print("[DEBUG] history data:", hist)
            if hist.empty:
                return None
            current_price = hist['Close'].iloc[-1]
            previous_close = hist['Close'].iloc[0] if len(hist) >= 2 else current_price
            return (
                f"股票代碼：{original}\n"
                f"現價：{current_price}\n"
                f"前收價：{previous_close}\n"
                f"市值：N/A"
            )
        except Exception as e:
            print("[DEBUG] Exception while fetching history:", e)
            return None

    current_price = info.get("regularMarketPrice", "N/A")
    previous_close = info.get("previousClose", "N/A")
    market_cap = info.get("marketCap", "N/A")
    return (
        f"股票代碼：{original}\n"
        f"現價：{current_price}\n"
        f"前收價：{previous_close}\n"
        f"市值：{market_cap}"
    )


@app.route("/webhook", methods=["POST"])
def webhook():
    """
    LINE Webhook 接收端點，設定為 /webhook
    """
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    except Exception as e:
        print("[DEBUG] Handler error:", e)
        abort(500)
    return "OK"


@app.route("/")
def index():
    """
    根目錄路由，用於健康檢查，避免 404
    """
    return "Hello, this is my LINE Bot application."


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text.strip()
    lower_text = text.lower()
    parts = text.split()

    # 如果用戶輸入 "menu" 或 "選單"，則回覆圖文選單（可自行修改內容）
    if lower_text in ("menu", "選單"):
        menu = TemplateSendMessage(
            alt_text="選單",
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
                        thumbnail_image_url="https://example.com/stock.png",
                        title="股票 Stock",
                        text="查看股票價格",
                        actions=[URIAction(label="查看", uri="https://yourwebsite.com/stock")],
                    ),
                    CarouselColumn(
                        thumbnail_image_url="https://example.com/finance-tips.png",
                        title="理財技巧 Finance tips",
                        text="獲取理財建議",
                        actions=[URIAction(label="獲取", uri="https://yourwebsite.com/finance-tips")],
                    ),
                    CarouselColumn(
                        thumbnail_image_url="https://example.com/rate-inquiry.png",
                        title="匯率查詢 Rate inquiry",
                        text="查詢今日匯率",
                        actions=[URIAction(label="查詢", uri="https://yourwebsite.com/rate-inquiry")],
                    ),
                    CarouselColumn(
                        thumbnail_image_url="https://example.com/stock-checkup.png",
                        title="股票健康檢查 Stock checkup",
                        text="查看股票健康狀況",
                        actions=[URIAction(label="檢查", uri="https://yourwebsite.com/stock-checkup")],
                    ),
                    CarouselColumn(
                        thumbnail_image_url="https://example.com/video.png",
                        title="影片 Video",
                        text="觀看金融相關影片",
                        actions=[URIAction(label="觀看", uri="https://yourwebsite.com/video")],
                    ),
                    CarouselColumn(
                        thumbnail_image_url="https://example.com/finance-website.png",
                        title="理財網站 Finance website",
                        text="訪問理財網站",
                        actions=[URIAction(label="訪問", uri="https://yourwebsite.com/finance-website")],
                    ),
                ]
            ),
        )
        line_bot_api.reply_message(event.reply_token, menu)
        return

    # 如果用戶輸入 "報價 <股票代號>" 或 "查股 <股票代號>"，則進行查詢
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

    # 如果用戶直接輸入純數字（如 "2330"），也視作查詢
    if text.isdigit():
        info = get_stock_info(text)
        if info:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=info))
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f"無法取得 {text.upper()} 的資料，請確認代碼是否正確。"),
            )
        return

    # 其他輸入回覆提示訊息
    help_msg = (
        "請輸入 'menu' 或 '選單' 來查看功能選單，\n"
        "或輸入 '報價 股票代碼' / '查股 股票代碼' 來查詢股票資訊，\n"
        "也可以直接輸入股票代號，例如：2330。"
    )
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=help_msg))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
