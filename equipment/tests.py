from django.test import TestCase

# Create your tests here.
from django.test import TestCase

# Create your tests here.
import json
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mes.settings")
django.setup()
import requests
import time
import hmac
import hashlib
import base64
import urllib.parse
from rest_framework.exceptions import ValidationError

"""
from spareparts.models import *
SpareType.objects.all().delete()
Spare.objects.all().delete()
SpareLocation.objects.all().delete()
SpareLocationBinding.objects.all().delete()
SpareInventory.objects.all().delete()
SpareInventoryLog.objects.all().delete()
"""
# url = 'https://oapi.dingtalk.com/robot/send?access_token=e789c3009a916030e74f8f740a792bd92f7c4e02f66d1ffcc3d16e35c23a5d15'
url = 'https://oapi.dingtalk.com/robot/send?access_token=7ab5afe7f9982ac5407ec619dfb1dd6a5e2a149fd191557527f027bc131d8635'
secret = 'SEC3c1de736eed3d8542c8116ebcea98bff51a158f7fc84fde2f4204b972ccc9706'


def send_ding_msg(url, secret, msg, isAtAll, atMobiles=None):
    """
    url:钉钉群机器人的Webhook
    secret:钉钉群机器人安全设置-加签
    msg:需要发送的数据
    isAtAll:是否@全体人员
    atMobiles:需要@人的手机号
    """

    timestamp = str(round(time.time() * 1000))
    secret = secret
    secret_enc = secret.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    url = url + '&' + f'timestamp={timestamp}&sign={sign}'
    # 中没有headers的'User-Agent'，通常会失败。
    headers = {"Content-Type": "application/json ;charset=utf-8"}

    if atMobiles:
        if not isinstance(atMobiles, list):
            raise ValidationError('atMobiles要么不传，要么给个列表')
    # 这里使用  文本类型
    data = {
        "msgtype": "text",
        "text": {
            "content": msg
        },
        "at": {  # @
            # "atMobiles": ["17356530633"],  # 专门@某一个人 同时下面的isAtAll要为False
            "atMobiles": atMobiles,  # 专门@某一个人 同时下面的isAtAll要为False
            "isAtAll": isAtAll  # 为真是@所有人
        }
    }

    try:
        r = requests.post(url, data=json.dumps(data), headers=headers)
        r = r.json()
    except Exception as e:
        r = None
    return r


mm = send_ding_msg(url=url, secret=secret, msg='1242421421', isAtAll=False, atMobiles=['17356530633'])
print(mm)
"""
当secret填写不对时，会提示如下信息
{'errcode': 310000, 'errmsg': 'sign not match, more: [https://ding-doc.dingtalk.com/doc#/serverapi2/qf2nxq]'}
当url填写不对时，会提示如下信息
{'errcode': 300001, 'errmsg': 'token is not exist'}
当发送成功时，会提示如下信息
{'errcode': 0, 'errmsg': 'ok'}
"""
