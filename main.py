# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 09:30:56 2024

@author: user
"""

from flask import Flask, request, abort, send_file
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, StickerSendMessage, VideoSendMessage, AudioSendMessage, ImageSendMessage
import os
import threading
import requests
import time
import pandas as pd
import mplfinance as mpf
from historical_data import get_klines_df

# 從環境變數中獲取 channel_token 和 channel_secret
channel_token = os.getenv('LINE_TOKEN')
channel_secret = os.getenv('LINE_SECRET')

app = Flask(__name__)
line_bot_api = LineBotApi(channel_token)
handler = WebhookHandler(channel_secret)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.error("Invalid signature. Check your channel secret and access token.")
        abort(400)
    except Exception as e:
        app.logger.error(f"Exception: {str(e)}")
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    try:
        if event.message.text == "貼圖":
            line_bot_api.reply_message(
                event.reply_token,
                StickerSendMessage(
                    package_id='1',
                    sticker_id='2'
                )
            )
        elif event.message.text == "影片":
            line_bot_api.reply_message(
                event.reply_token,
                VideoSendMessage(
                    original_content_url='https://www.w3schools.com/html/mov_bbb.mp4',
                    preview_image_url='https://www.w3schools.com/html/pic_trulli.jpg'
                )
            )
        elif event.message.text == "音訊":
            line_bot_api.reply_message(
                event.reply_token,
                AudioSendMessage(
                    original_content_url='https://filesamples.com/samples/audio/m4a/sample4.m4a',
                    duration=100000
                )
            )
        elif event.message.text == "圖片":
            line_bot_api.reply_message(
                event.reply_token,
                ImageSendMessage(
                    original_content_url='https://picsum.photos/200/300',
                    preview_image_url='https://picsum.photos/200/300'
                )
            )
        elif event.message.text == "K線圖":
            # 生成K線圖
            symbol = "BTCUSDT"
            interval = "6h"
            klines = get_klines_df(symbol, interval)
            data = klines.copy()
            data['floor'] = data.rolling(60)['low'].min().shift(1)
            data['ceil'] = data.rolling(60)['high'].max().shift(1)
            addp = []
            addp.append(mpf.make_addplot(data['floor']))
            addp.append(mpf.make_addplot(data['ceil']))
            mcolor = mpf.make_marketcolors(up='r', down='g', inherit=True)
            mstyle = mpf.make_mpf_style(base_mpf_style='yahoo', marketcolors=mcolor)
            chart_path = 'chart.png'
            mpf.plot(data, style=mstyle, addplot=addp, type='candle', savefig=chart_path)

            # 發送K線圖
            line_bot_api.reply_message(
                event.reply_token,
                ImageSendMessage(
                    original_content_url=f'https://line-bot-app.onrender.com/{chart_path}',
                    preview_image_url=f'https://line-bot-app.onrender.com/{chart_path}'
                )
            )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=event.message.text)
            )
    except Exception as e:
        app.logger.error(f"Exception in handle_message: {str(e)}")

@app.route("/")
def index():
    return "Hello, this is the Line bot server."

@app.route("/chart.png")
def get_chart():
    return send_file("chart.png", mimetype="image/png")

def run():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    while True:
        try:
            requests.get('https://line-bot-app.onrender.com')
        except Exception as e:
            app.logger.error(f"Keep-alive error: {str(e)}")
        time.sleep(600)  # 每10分鐘ping一次

if __name__ == "__main__":
    t = threading.Thread(target=keep_alive)
    t.start()
    run()
