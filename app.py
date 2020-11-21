import numpy as np

from flask import Flask, request, abort
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (MessageEvent, TextMessage, TextSendMessage, ImageMessage, ImageSendMessage)
from keras.models import load_model
from keras.preprocessing import image

app = Flask(__name__)

ACCESS_TOKEN = "ZWqC9dOrT8Rpi8YHLYkZiPT7IMB0TTiOlhgEM3qeQrEMwInbLhRAqo3wqbesJea5KIuUoa/9+TdFcxMeNo/g0VyiOKEm7pgq41jeYVy+gsqX8aVNyvkkJoP0pqiAhStUvWGK1MfATE6lzHhsIvIZDAdB04t89/1O/w1cDnyilFU="
SECRET = "818b6f3efb27d959f5e315aaa7886864"

FQDN = "https://kinoko-takenoko.herokuapp.com"


line_bot_api = LineBotApi(ACCESS_TOKEN)
handler = WebhookHandler(SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Requestbody: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return'OK'

#LINEに画像が送られてきた時の発生イベント
@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    message_content = line_bot_api.get_message_content(event.message.id)
    with open("static/"+event.message.id+".jpg", "wb") as f:
        f.write(message_content.content)

        test_url = "./static/"+event.message.id+".jpg"
##########ここからAIモデル＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃
        img = image.load_img(test_url, target_size=(150, 150))
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = x / 255.0

        model = load_model('okashi.h5')
        result_predict = model.predict(x)

        if result_predict < 0.5:
            result_predict = 1 - result_predict
            okashi = "きのこの山"
            result_predict = result_predict * 100
            per = '{:.1f}'.format(result_predict)
        elif result_predict >= 0.5:
            okashi = "たけのこの里"
            result_predict = result_predict * 100
            per = '{:.1f}'.format(result_predict)
        text = "これは"+ per+ "%の確率で" + okashi + "です。"
##############################################################
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=text))
      
if __name__ == "__main__":
    app.run()
