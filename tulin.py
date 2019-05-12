import json
import random
import urllib.request

api_url = "http://openapi.tuling123.com/openapi/api/v2"
data = {
    'key'    : '79dda117bd6545c29f45d8da945bfdef', # 如果这个Tuling Key不能用，那就换一个
    'info'   : 'hello', # 这是我们发出去的消息
    'userid' : 'wechat-robot', # 这里你想改什么都可以
}
def askTuling(text_input):
    req = {
        "perception":
        {
            "inputText":
            {
                "text": text_input
            },

            "selfInfo":
            {
                "location":
                {
                    "city": "上海",
                    "province": "上海",
                    "street": "文汇路"
                }
            }
        },

        "userInfo":
        {
            "apiKey": "79dda117bd6545c29f45d8da945bfdef",
            "userId": "b576d4b011081083"
        }
    }
    # print(req)
    # 将字典格式的req编码为utf8
    req = json.dumps(req).encode('utf8')
    # print(req)
    http_post = urllib.request.Request(api_url, data=req, headers={'content-type': 'application/json'})
    response = urllib.request.urlopen(http_post)
    response_str = response.read().decode('utf8')
    # print(response_str)
    response_dic = json.loads(response_str)
    return_msg = {}
    print(response_dic)
    if(response_dic['intent']['code'] == 10003):
        try:
            return_msg['text'] = response_dic['results'][0]['values']['text']
            number = random.randint(0, len(response_dic['results'][1]['values']['news']) - 1)
            return_msg['news'] = response_dic['results'][1]['values']['news'][number]
        except:
            print("无法找到")
            return None
        return return_msg
    elif(response_dic['intent']['code'] == 10014):
        try:
            return_msg['text'] = response_dic['results'][1]['values']['text']
            return_msg['url'] = response_dic['results'][0]['values']['url']
        except:
            print("无法找到")
            return None
        return return_msg

    return None


#askTuling("小猫的图片")