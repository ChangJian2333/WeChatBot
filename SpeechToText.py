import os
import re
from aip import AipSpeech
from ffmpy3 import FFmpeg

def mp3_change_pcm(mp3_path):
    ff = FFmpeg(
        inputs={mp3_path: None},
        outputs={
            './target.pcm':'-acodec pcm_s16le -f s16le -ac 1 -ar 16000'
        }
    )
    ff.run()

# 读取文件
def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()

def voice_recongnition(pcm_file):
    APP_ID = '16184075'
    API_KEY = 'OY4u5LVYfQUPB3oLEcfm1DNP'
    SECRET_KEY = 'm3MQrGkLTXGO3mgnljXtOBSXB8dG8HGp'
    client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)
    client.setConnectionTimeoutInMillis(5000)
    client.setSocketTimeoutInMillis(10000)
    # 识别本地文件
    try:
        results = client.asr(get_file_content(pcm_file), 'pcm', 16000, {'dev_pid': 1536,})
    except:
        print("无法连接服务器")
        return  [None]
    return results['result']

# 语音识别启动函数
def voice_recon_run(mp3_path):
            if 'target.pcm' in os.listdir():
                os.remove(r'./target.pcm')
            mp3_change_pcm(mp3_path)
            voice_recon_text = voice_recongnition(r'./target.pcm')
            for mp3 in os.listdir():
                if(mp3[-3:] == 'mp3'):
                    os.remove(mp3)
            os.remove(r'./target.pcm')
            return voice_recon_text[0]
