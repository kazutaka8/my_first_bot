import os
from datetime import datetime, timezone, timedelta
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from dotenv import load_dotenv

load_dotenv(override=True)

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ["ACCESS_TOKEN"])
handler = WebhookHandler(os.environ["CHANNEL_SECRET"])


@app.route("/")
def index():
    return "You call index()"


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    recieved_msg = event.message.text
    ex_recieved_msg = "！".join(recieved_msg)
    reply_msg = f"{ex_recieved_msg}！"

    # 送信時刻を取得し、日本時間に変換
    timestamp = event.timestamp  # ミリ秒
    dt = datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc) + timedelta(hours=9)  # 日本時間(JST)
    dt_str = dt.strftime("%Y-%m-%d %H:%M:%S")

    # 返信メッセージに日時を追加
    reply_msg += f"\n送信日時: {dt_str}"

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_msg))


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
