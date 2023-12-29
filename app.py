from certifi import contents
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import FlexSendMessage, TextSendMessage, MessageEvent, TextMessage, PostbackEvent


import logging

#主程式
import os

app = Flask(__name__)

# 部署上render.com時要註解
# from dotenv import load_dotenv
# load_dotenv('dev.env')

# Channel Access Token
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
# Channel Secret
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))

@app.route("/alive",methods=['GET','POST'])
def alive():
    return "alive"

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

 
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

def generate_main_menu():
    return {
        "type": "bubble",
        "size": "mega",
        "hero": {
            "type": "image",
            "url": "https://scdn.line-apps.com/n/channel_devcenter/img/fx/01_1_cafe.png",
            "margin": "none",
            "size": "full",
            "animated": False,
            "backgroundColor": "#999999",
            "position": "relative"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
            {
                "type": "button",
                "action": {
                    "type": "postback",
                    "label": "時間元件",
                    "data": "dateTimePick",
                    "displayText": "時間元件"
                }
            },
            {
                "type": "button",
                "action": {
                    "type": "uri",
                    "label": "Pollex",
                    "uri": "https://www.pollex.com.tw/#!/"
                }
            }
            ]
        }
        }

def generate_goods_json():
    return {
        "type": "bubble",
        "hero": {
            "type": "image",
            "url": "https://scdn.line-apps.com/n/channel_devcenter/img/fx/01_2_restaurant.png",
            "size": "full",
            "aspectRatio": "20:13",
            "aspectMode": "cover",
            "action": {
            "type": "uri",
            "uri": "https://linecorp.com"
            }
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "action": {
            "type": "uri",
            "uri": "https://linecorp.com"
            },
            "contents": [
            {
                "type": "text",
                "text": "Brown's Burger",
                "size": "xl",
                "weight": "bold"
            },
            {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": []
            },
            {
                "type": "text",
                "text": "Sauce, Onions, Pickles, Lettuce & Cheese",
                "wrap": True,
                "color": "#aaaaaa",
                "size": "xxs"
            }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "contents": [
            {
                "type": "button",
                "style": "primary",
                "color": "#905c44",
                "margin": "xxl",
                "action": {
                "type": "uri",
                "label": "Add to Cart",
                "uri": "https://linecorp.com"
                }
            }
            ]
        }
        }
 
def generate_date_pick():
    return {
        "type": "bubble",
        "size": "mega",
        "hero": {
            "type": "box",
            "layout": "horizontal",
            "contents": [
            {
                "type": "text",
                "text": "選個時間吧",
                "align": "center",
                "size": "xxl",
                "color": "#000000"
            }
            ],
            "position": "relative",
            "action": {
                "type": "message",
                "label": "action",
                "text": "hello"
            },
            "backgroundColor": "#0492b3",
            "spacing": "lg",
            "flex": 2,
            "height": "50px",
            "alignItems": "center"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [{
                "type": "button",
                "action": {
                "type": "datetimepicker",
                "label": "請選擇時間",
                "data": "pickTime",
                "mode": "date"
                },
                "height": "sm"
            }],
            "height": "80px",
            "alignItems": "center",
            "justifyContent": "center"
        }
    }

#訊息傳遞區塊
##### 基本上程式編輯都在這個function #####
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = TextSendMessage(text=event.message.text)

    if message.text == 'menu':
        flex_message = FlexSendMessage(alt_text="hello", contents=generate_main_menu())
        line_bot_api.reply_message(
            event.reply_token,
            flex_message
        )
    else :
        line_bot_api.reply_message(event.reply_token,message)

    app.logger.info("show event: ")
    app.logger.info(event)
    
@handler.add(PostbackEvent)
def handle_postback(event):
    
    postback_data = event.postback.data
    postback_params = event.postback.params
    app.logger.info("show postback_params start")
    app.logger.info(postback_params)
    app.logger.info("show postback_params end")

    if postback_data == 'dateTimePick':

        reply_message = FlexSendMessage(alt_text="time",contents=generate_date_pick())
        line_bot_api.reply_message(event.reply_token, reply_message)

    elif postback_data == 'pickTime':

        message_content = f"這是你選擇的時間:  {postback_params['date']}"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message_content))

    # line_bot_api.reply_message(event.reply_token, reply_message)


gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    