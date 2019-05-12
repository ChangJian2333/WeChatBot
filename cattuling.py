import itchat
import time
import os
import SpeechToText
import re
import random
import tulin
import requests

from itchat.content import  PICTURE, VIDEO,MAP, CARD, SHARING, RECORDING

document = "1.输入'上传'就可以开始上传我的照片或视频\n 2.输入'停止上传'停止上传我的照片或视频\n 3.输入'你的照片'就可以获取我最近的照片" \
           "\n4.输入'你的视频'就可以获取我最近的视频 \n5. 输入'还要照片'就可以继续获得随机的照片\n6.输入'还要视频'就可以继续获得随机的视频\n7.还可以和交流 \n8.输入'cat'获得提示信息"
documentoforGroup = "1.输入'你的照片'就可以获取我最近的照片. \n2.输入'你的视频'就可以获取我最近的视频 \n3.还可以和交流\n4. 输入'还要照片'就可以继续获得随机的照片\n5.输入'还要视频'就可以继续获得随机的视频 \n6.@我获得提示信息"


contact = set()
contactMessage = {}#设置上传信息，判断图片是否需要上传
recordtime = {}#5分钟，五分钟内没有上传图片，就终端上传
userId = ''#记录谁给我发消息，让小冰回答

#与人联系###########################################支持文本图片视频语音
#收到文字
@itchat.msg_register(itchat.content.TEXT)
def msgFromcontact(msg):
    if(msg['FromUserName'] not in contact):
        itchat.send_msg(document, toUserName=msg['FromUserName'])
        contact.add(msg['FromUserName'])
    if(msg['Text'] == 'cat'):
        itchat.send_msg(document, toUserName=msg['FromUserName'])
    elif(msg['Text'] == "上传"):
        itchat.send_msg("主人,我已经准备好了，可以上传我可爱的照片或视频了", toUserName=msg['FromUserName'])
        contactMessage[msg['FromUserName']] = True
        recordtime[msg['FromUserName']] = int(time.strftime('%m%d%H%M',time.localtime(time.time())))
    elif(msg['Text'] == "停止上传"):
        itchat.send_msg("主人，上传都结束，记得下次把我拍的美美的，再上传哦", toUserName=msg['FromUserName'])
        contactMessage[msg['FromUserName']] = False
        recordtime.pop(msg['FromUserName'], 0)
    elif(msg['Text'] == '你的照片'):
        sendImage(msg)
    elif(msg['Text'] == '你的视频'):
        sendVideo(msg)
    elif(msg['Text'] == '还要照片'):
        sendImageRandom(msg)
    elif(msg['Text'] == '还要视频'):
        sendVideoRandom(msg)
    else:
        xbAnswer(msg)

#收到名片
@itchat.msg_register(CARD)
def add_card(msg):
    itchat.add_friend(userName=msg['Text']['UserName'])
    itchat.send_msg("主人， 已经发出申请添加好友", toUserName=msg['FromUserName'])

#收到语音
@itchat.msg_register([RECORDING])
def otherFromcontact(msg):
    xbAnswer(msg)

#收到位置消息
@itchat.msg_register(MAP)
def recordMap(msg):
    itchat.send_msg("主人，我看不懂地图哦!", toUserName=msg['FromUserName'])

#收到分享
@itchat.msg_register(SHARING)
def recordMap(msg):
    itchat.send_msg("主人，不敢点，不敢点，我怕有毒呢!", toUserName=msg['FromUserName'])

#收到图片
#收到视频
@itchat.msg_register([itchat.content.PICTURE, itchat.content.VIDEO])
def getimage(msg):
    for i in recordtime:
        if int(time.strftime('%m%d%H%M', time.localtime(time.time()))) - recordtime[i] >= 5:
            contactMessage[i] = False
            recordtime.pop(i, 0)
            itchat.send_msg("主人，上传都结束，记得下次把我拍的美美的，再上传哦", toUserName=i)
    if(contactMessage.setdefault(msg['FromUserName'], False)):
        if(msg['Type'] == 'Picture'):
            msg['Text'](os.getcwd() + "/picture/" + msg['FileName'])
        else:
            msg['Text'](os.getcwd() + "/video/" + msg['FileName'])
        itchat.send_msg("上传成功", toUserName=msg['FromUserName'])
        recordtime[msg['FromUserName']] = int(time.strftime('%m%d%H%M', time.localtime(time.time())))
    else:
        xbAnswer(msg)



#发送照片
def sendImage(msg):
    now = time.strftime('%Y%m%d-%H%M%S',time.localtime(time.time()))
    file = os.listdir(os.getcwd() + "/picture")
    i = 0
    file.reverse()
    for pic in file:
        if(pic[0:6] == now[2:8]):
            i += 1
            itchat.send("@img@%s" % (os.getcwd() + "/picture/" + pic), toUserName=msg['FromUserName'])
        if(i >= 3):
            break
    if(i == 0):
        itchat.send_msg("今天的我还没自拍,给你看前几天的吧", toUserName=msg['FromUserName'])
        if(len(file) == 0):
            itchat.send_msg("我可伤心了，我还一张照片都没有呢", toUserName=msg['FromUserName'])
        else:
            i = 0
            for pic in file:
                if(i < 3):
                    i += 1
                    itchat.send("@img@%s" % (os.getcwd() + "/picture/" + pic), toUserName=msg['FromUserName'])

def sendImageRandom(msg):
    file = os.listdir(os.getcwd() + "/picture")
    file.reverse()
    num = random.randint(0, len(file) - 1)
    itchat.send("@img@%s" % (os.getcwd() + "/picture/" + file[num]), toUserName=msg['FromUserName'])

#发送视频
def sendVideo(msg):
    now = time.strftime('%Y%m%d-%H%M%S', time.localtime(time.time()))
    file = os.listdir(os.getcwd() + "/video")
    i = 0
    file.reverse()
    for video in file:
        if (video[0:6] == now[2:8]):
            i += 1
            itchat.send("@vid@%s" % (os.getcwd() + "/video/" + video), toUserName=msg['FromUserName'])
        if(i >= 1):
            break
    if (i == 0):
        itchat.send_msg("今天的我还没自拍,给你看前几天的吧", toUserName=msg['FromUserName'])
        if (len(file) == 0):
            itchat.send_msg("我可伤心了，我还一个视频都没有呢", toUserName=msg['FromUserName'])
        else:
            i = 0
            for video in file:
                if (i < 1):
                    i += 1
                    itchat.send("@vid@%s" % (os.getcwd() + "/video/" + video), toUserName=msg['FromUserName'])

def sendVideoRandom(msg):
    file = os.listdir(os.getcwd() + "/video")
    file.reverse()
    num = random.randint(0, len(file) - 1)
    itchat.send("@vid@%s" % (os.getcwd() + "/video/" + file[num]), toUserName=msg['FromUserName'])
#####################################################################################################
##群聊
@itchat.msg_register(itchat.content.TEXT, isGroupChat=True)
def text_reply(msg):
    if(msg.isAt):
        if (msg['FromUserName'] not in contact):
            itchat.send_msg(documentoforGroup, toUserName=msg['FromUserName'])
            contact.add(msg['FromUserName'])
        msg['Text'] = msg['Text'][len(msg['Text'].split()[0]) + 1:]
        if (msg['Text'] == '你的照片'):
            sendImage(msg)
        elif(msg['Text'] == '你的视频'):
            sendVideo(msg)
        elif(msg['Text'] == ''):
            itchat.send_msg(documentoforGroup, toUserName=msg['FromUserName'])
        elif (msg['Text'] == '还要照片'):
            sendImageRandom(msg)
        elif (msg['Text'] == '还要视频'):
            sendVideoRandom(msg)
        else:
            if ('http' in msg['Text']):
                dealLink(msg)
            xbAnswer(msg)
######################################################################################################3
#智能回复人video recording image text
def dealLink(msg):
    link = re.findall('<a href=.*?</a>', msg['Text'])
    for alink in link:
        tmp = re.findall('http.*?"', alink)[0][:-1]
        msg['Text'] = re.sub('<a href=.*?</a>', ' ' + tmp, msg['Text'], count=1)

def xbAnswer(msg):
    global userId
    userId = msg['FromUserName']
    xb = itchat.search_mps(name='小冰')[0]
    isGroup(msg)
    if msg['Type'] == 'Picture':
        msg['Text'](msg['FileName'])
        itchat.send_image(msg['FileName'], toUserName=xb['UserName'])
        os.remove(msg['FileName'])
    elif msg['Type'] == 'Video':
        msg['Text'](msg['FileName'])
        itchat.send_video(msg['FileName'], toUserName=xb['UserName'])
        os.remove(msg['FileName'])
    elif msg['Type'] == 'Recording':
        msg['Text'](msg['FileName'])#保存为mp3
        voice = SpeechToText.voice_recon_run(msg['FileName'])
        if(voice == None):
            itchat.send_msg("我现在听力不好", toUserName=msg['FromUserName'])
        else:
            itchat.send_msg(voice, toUserName=xb['UserName'])
    else:
        if('http' in msg['Text']):
            dealLink(msg)
        if("新闻" in msg['Text']):
            news = tulin.askTuling(msg['Text'])
            if(news != None):
                itchat.send_msg(news['text'], toUserName=msg['FromUserName'])
                itchat.send_msg(news['news']['name'], toUserName=msg['FromUserName'])
                r = requests.get("http:" + news['news']['icon'])
                with open("tmp.jpg", "wb") as f:
                    f.write(r.content)
                itchat.send_image("tmp.jpg", toUserName=msg['FromUserName'])
                os.remove("tmp.jpg")
                itchat.send_msg("链接 : " + news['news']['detailurl'], toUserName=msg['FromUserName'])
            else:
                itchat.send_msg(msg['Text'], toUserName=xb['UserName'])
        elif ("图片" in msg['Text']):
            pic = tulin.askTuling(msg['Text'])
            if (pic != None):
                itchat.send_msg(pic['text'], toUserName=msg['FromUserName'])
                itchat.send_msg("链接 : " + pic['url'], toUserName=msg['FromUserName'])
            else:
                itchat.send_msg(msg['Text'], toUserName=xb['UserName'])

        else:
            itchat.send_msg(msg['Text'], toUserName=xb['UserName'])


@itchat.msg_register([itchat.content.TEXT, PICTURE, VIDEO, MAP, CARD, SHARING, RECORDING], isMpChat=True)
def AIreply(msg):
    print("收到")
    if msg['Type'] == 'Picture':
        msg['Text'](msg['FileName'])
        itchat.send_image(msg['FileName'], toUserName=userId)
        os.remove(msg['FileName'])
    elif msg['Type'] == 'Video':
        msg['Text'](msg['FileName'])
        itchat.send_video(msg['FileName'], toUserName=userId)
        os.remove(msg['FileName'])
    elif msg['Type'] == 'Recording':
        msg['Text'](msg['FileName'])#保存为mp3
        itchat.send_file(msg['FileName'], toUserName=userId)
        os.remove(msg['FileName'])
    elif msg['Type'] == 'Text':
        if('http' in msg['Text']):
            dealLink(msg)
        itchat.send_msg(msg['Text'], toUserName=userId)
    elif msg['Type'] == 'Sharing':
        print("音乐")
        message = re.findall('<url>.*</url>', msg['Content'])[0][5:-6]
        if(message[0:4] == "http"):
            itchat.send(message, toUserName=userId)
    else:
        pass

def isGroup(msg):
    if 'ActualNickName' in msg:
        itchat.send_msg("@" + msg['ActualNickName'], toUserName=msg['FileName'])

random.seed(time.time())
itchat.auto_login(enableCmdQR=2, hotReload=True)
itchat.run()