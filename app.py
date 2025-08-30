import os
import requests
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from dotenv import load_dotenv

load_dotenv(override=True)

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ["ACCESS_TOKEN"])
handler = WebhookHandler(os.environ["CHANNEL_SECRET"])

# 都道府県リスト
PREFECTURES = [
    "北海道", "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県",
    "茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県",
    "新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県", "岐阜県",
    "静岡県", "愛知県", "三重県", "滋賀県", "京都府", "大阪府", "兵庫県",
    "奈良県", "和歌山県", "鳥取県", "島根県", "岡山県", "広島県", "山口県",
    "徳島県", "香川県", "愛媛県", "高知県", "福岡県", "佐賀県", "長崎県",
    "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県"
]

def find_prefecture(text):
    """テキストから都道府県名を検索"""
    for prefecture in PREFECTURES:
        if prefecture in text:
            return prefecture
    return None

def get_news_for_prefecture(prefecture):
    """指定された都道府県のニュースを取得"""
    try:
        # NewsAPIを使用（無料版は制限あり）
        api_key = os.environ.get("NEWS_API_KEY")
        if not api_key:
            return "ニュースAPI設定が見つかりません。"
        
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": prefecture,
            "language": "ja",
            "sortBy": "publishedAt",
            "pageSize": 5,
            "apiKey": api_key
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get("articles", [])
            
            if not articles:
                return f"{prefecture}に関するニュースが見つかりませんでした。"
            
            news_list = []
            for article in articles[:3]:  # 最新3件
                title = article.get("title", "")
                url = article.get("url", "")
                if title and url:
                    news_list.append(f"📰 {title}\n{url}")
            
            if news_list:
                return f"{prefecture}の最新ニュース:\n\n" + "\n\n".join(news_list)
            else:
                return f"{prefecture}に関するニュースが見つかりませんでした。"
        else:
            return "ニュースの取得に失敗しました。"
            
    except Exception as e:
        return f"エラーが発生しました: {str(e)}"


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
    received_msg = event.message.text
    
    # 都道府県名を検索
    prefecture = find_prefecture(received_msg)
    
    if prefecture:
        # 都道府県が見つかった場合、ニュースを取得
        reply_msg = get_news_for_prefecture(prefecture)
    else:
        # 都道府県が見つからない場合、使用方法を案内
        reply_msg = "都道府県名を入力してください。\n例: 東京都、大阪府、北海道"
    
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_msg))


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
