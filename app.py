import os
from flask import Flask, request, abort
import yfinance as yf
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# 直接硬編碼 LINE Bot 認證資訊（正式環境建議以環境變數管理）
line_bot_api = LineBotApi(
    'T/EUr80xzlGCYpOUBsuORZdWpWwl/EYMxZRgnyorALxmo0xp5ti+2ELOII85fYQZ1bf/tNbOy3Y2T3GFPKBrOGsJd1dkQ8t2Rhkh5Fc9SSq1Jn/+dTZljEyGzEdUfoL1n0LsPdKagWWHk5ZEyd8aygdB04t89/1O/w1cDnyilFU='
)
handler = WebhookHandler('a2180e40b0a6c2ef14fde47b59650d60')

def get_stock_info(ticker: str) -> str:
    """
    根據股票代號取得股票資訊。
    
    1. 若用戶輸入純數字（例如 "2330"），則自動加上 .TW 後綴查詢台灣股票資料。
    2. 依靠最近 5 天的歷史資料取得最後一天的收盤價作為現價，
       並取倒數第二天的收盤價作為前收價。
    3. 若歷史資料不足，則回傳 None。
    """
    original = ticker.upper()
    # 若輸入為純數字則自動加上 .TW 後綴
    if original.isdigit():
        ticker = original + ".TW"
    else:
        ticker = original

    # Debug 輸出（可於 Render 日誌觀察）
    print("[DEBUG] Fetching ticker:", ticker)
    try:
        stock = yf.Ticker(ticker)
        # 取近 5 天歷史資料
        hist = stock.history(period="5d")
        print("[DEBUG] history data for", ticker, ":\n", hist)
        if hist.empty or len(hist) < 2:
            return None
        current_price = hist['Close'].iloc[-1]
        previous_close = hist['Close'].iloc[-2]
        return (
            f"股票代碼：{original}\n"
            f"現價：{current_price}\n"
            f"前收價：{previous_close}\n"
            f"市值：N/A"
        )
    except Exception as e:
        print("[DEBUG] Exception in get_stock_info:", e)
        return None

@app.route("/webhook", methods=["POST"])
def webhook():
    """
    LINE Webhook 接收端點，設定為 /webhook  
    請確認 LINE Webhook URL 於 LINE Developer Console 設定為：
    https://a-8edl.onrender.com/webhook
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
    根目錄路由，用於健康檢查，避免回傳 404
    """
    return "Hello, this is my LINE Bot application."

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text.strip()
    parts = text.split()
    
    # 如果用戶輸入格式為 "報價 股票代號" 或 "查股 股票代號"
    if len(parts) >= 2 and parts[0] in ("報價", "查股"):
        ticker = parts[1]
        info = get_stock_info(ticker)
        if info:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=info))
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f"無法取得 {ticker.upper()} 的資料，請確認代碼是否正確。")
            )
        return

    # 如果用戶直接輸入單一股票代號，例如 "2330"
    if len(parts) == 1:
        info = get_stock_info(text)
        if info:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=info))
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f"無法取得 {text.upper()} 的資料，請確認代碼是否正確。")
            )
        return

    # 其他情況回覆提示訊息
    help_msg = "請直接輸入股票代號，例如：2330"
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=help_msg))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
