#linebot相關Package
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, PostbackEvent, FollowEvent,
    TextMessage, TextSendMessage, FlexSendMessage)
app = Flask(__name__)
#追加功能相關Package
import re
import json
import random
import os

# 必須放上自己的Channel Access Token、Channel Secret
channel_access_token = 'channel_access_token'
channel_secret = 'channel_secret'

#常用定義/功能
app = Flask(__name__)
line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)
game_key = {}
join_list = {}

#常用模組
#文字訊息
def TextMsg(event, text): 
    line_bot_api.reply_message(
            event.reply_token,
            TextMessage(text= text)
        )
#推播訊息
def PushMsg(uid, text): 
    line_bot_api.push_message(to= uid, messages= TextSendMessage(text= text))
def MultMsg(uid, text): 
    line_bot_api.multicast(to= uid,messages= TextSendMessage(text= text))
#客製化訊息
def FlexMsg(event,text, flex): 
    line_bot_api.reply_message(
        event.reply_token,                    
        messages=FlexSendMessage(
            alt_text= text,
            contents= json.loads(json.dumps(flex, ensure_ascii=False))
          )
        )

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)        
    except InvalidSignatureError:
        abort(400)
    return 'OK'

#啟動訊息，管理員帳號
"""
admin_id = ['LINE_UID']
for i in admin_id:
    PushMsg(i, '你可以開始了')
"""
   
#加好友回報ID
@handler.add(FollowEvent)
def handle_join(event):
    global join_list
    profile_user = line_bot_api.get_profile(event.source.user_id) 
    join_list[event.source.user_id] = profile_user.display_name
    TextMsg(event, '週週抽獎抽不完~ 請輸入遊戲名字~ \n例如 : 白涵公主,加入王國')
    return

#訊息傳遞區塊
@handler.add(MessageEvent, message=TextMessage)
def reply(event):
    global game_key, join_list
    msg = event.message.text
    profile_user = line_bot_api.get_profile(event.source.user_id) 
    if re.search('加入王國', msg):
        text = event.source.user_id \
            + '\n' \
            + profile_user.display_name \
            + '\n' \
            + msg.split(',')[0] \
            + '\n大頭貼 : ' \
            + profile_user.picture_url
        join_list[event.source.user_id] = '{name},{game}'.format(name= profile_user.display_name, game = msg.split(',')[0])
        MultMsg(admin_id, text)
        TextMsg(event, profile_user.display_name+ ' 歡迎加入王國抽獎名單~')
        return
    if re.search('抽獎', msg):
        game_split = msg.split(',')
        if game_split[0] == '舉辦抽獎' :
              room = ''
              for i in range(0,6):           
                  room += str(random.randint(0,9))
              while room in game_key.keys() :
                  room += str(random.randint(0,9))
             
              game_key[room] = {
                            'game_list' : {},
                            'game_draw' : [],
                            'game_end' : False, 
                            'game_max' : game_split[2], 
                            'game_pool' : game_split[1]
                            }
              game = {}
              game = {                    
                  'type': 'bubble',
                  'size' : 'giga',
                  'hero': {
                        'type': 'box',
                        'layout': 'vertical',
                        'contents': []
                           },
                  'header': {
                        'type': 'box',
                        'layout': 'vertical',
                        'contents': [{
                            'type': 'image',
                            'url': 'https://i.imgur.com/IoPqQPZ.png',
                            'size': 'full',
                            'aspectMode': 'cover'
                            }]
                        },
                  'body': {
                        'type': 'box',
                        'layout': 'vertical',
                        'contents': []
                        },                      
                  'footer': {                      
                        'type': 'box',
                        'layout': 'vertical',
                        'backgroundColor': '#fffdeb',
                        'contents': [
                                   {
                                'type': 'box',
                                'layout': 'horizontal',
                                'backgroundColor': '#fffdeb',
                                'contents': [
                                    {
                                    'type': 'button',
                                    'color' : '#ffbc47',
                                    'style' : 'primary',
                                    'action': {
                                        'type': 'postback',
                                        'label': '參加抽獎',
                                        'data': '抽獎編號-參加-' + room
                                           }
                                        }
                                    ,{
                                    'type': 'button',
                                    'color' : '#ffbc47',
                                    'style' : 'primary',
                                    'action': {
                                            'type': 'postback',
                                            'label': '取消抽獎',
                                            'data': '抽獎編號-取消-' + room
                                            }
                                        }
                                    ,{
                                    'type': 'button',
                                    'color' : '#ffbc47',
                                    'style' : 'primary',
                                    'action': {
                                            'type': 'postback',
                                            'label': '參加名單',
                                            'data': '抽獎編號-名單-' + room
                                            }
                                        }
                                    ]
                                   },
                                 {
                                'type': 'box',
                                'layout': 'horizontal',
                                'backgroundColor': '#ffe6cc',
                                'contents': [
                                        {
                                    'type': 'button',
                                    'color' : '#ababab',
                                    'style' : 'primary',
                                    'action': {
                                        'type': 'postback',
                                        'label': '開獎',
                                        'data': '抽獎編號-開獎-' + room
                                            }
                                        }
                                    ]  
                                }
                            ]
                        }
                    }
              tittle = {
                    'type': 'text',
                    'text': game_split[1] + ' 抽取人數 : '+ game_split[2] + ' ----開始報名',
                    'weight': 'bold',
                    'color': '#171717',
                    'size': 'sm'
                        }
              separator = {'type': 'separator'}
              exp = {
                    'type': 'text',
                    'text': '代抽方式 : 遊戲名稱,{room},參加抽獎'.format(room = room),
                    'weight': 'bold',
                    'color': '#171717',
                    'size': 'sm'
                        }
              game['body']['contents'].append(tittle)
              game['body']['contents'].append(separator)
              game['body']['contents'].append(exp)
              FlexMsg(event, '抽獎編號' + room, game)
              return
        elif game_split[1] in game_key.keys() :
              if game_split[2] == '參加抽獎':
                  game_key[game_split[1]]['game_list'][game_split[0]] = game_split[0]
                  TextMsg(event, game_split[0] +'----報名成功')
                  return
              elif game_split[2] == '取消抽獎':
                  del game_key[game_split[1]]['game_list'][game_split[0]]
                  TextMsg(event, game_split[0] +'----刪除成功')            
                  return

@handler.add(PostbackEvent)
def Postback_game(event):
    global game_key
    val = event.postback.data
    profile_user = line_bot_api.get_profile(event.source.user_id) 
    if re.search('抽獎編號', val):
        ordr = val.split('-')[1]
        room = val.split('-')[2]
        if room not in game_key.keys():
            return
        if ordr == '參加':
            game_key[room]['game_list'][event.source.user_id] = profile_user.display_name
            TextMsg(event, profile_user.display_name +'----抽獎編號{room}--報名成功'.format(room = room))
            return
        elif ordr == '取消':
            del game_key[room]['game_list'][event.source.user_id]
            TextMsg(event, profile_user.display_name +'----抽獎編號{room}--刪除成功'.format(room = room))
            return
        elif ordr == '名單':
            game_list = '\n'.join(game_key[room]['game_list'].values())
            text= game_key[room]['game_pool'] \
                +'----抽取人數 : ' \
                + game_key[room]['game_max'] \
                +'\n參加名單\n--------\n' \
                + game_list   
            TextMsg(event, text)
            return
        elif ordr == '開獎' :
            if event.source.user_id not in admin_id:
                return
            elif game_key[room]['game_end'] :
                return
            elif len(game_key[room]['game_list']) < int(game_key[room]['game_max']) :
                TextMsg(event, '參加人數不足')
                return
            else:
                r = random.sample(game_key[room]['game_list'].keys(), k = int(game_key[room]['game_max']))
                for num, i in enumerate(r):
                    name = game_key[room]['game_list'][i]
                    game_key[room]['game_draw'].append(name) 
                    if len(i) == 33 :
                        try :
                            text= game_key[room]['game_pool'] \
                                +'----抽獎編號 : ' \
                                + room \
                                + '\n恭喜 {name} 中獎----請投標由左到右數來第{num}個'.format(num = str(num+1), name = name)
                            PushMsg(event, i, text)                       
                        except :
                            print('#error_uid')                            
            game_list = '\n'.join(game_key[room]['game_draw'])
            text = game_key[room]['game_pool'] \
                 + '----' \
                 + room \
                 + '\n得獎名單\n--------\n' \
                 + game_list
            game_key[room]['game_end'] = True
            TextMsg(event, text)
            return    

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
