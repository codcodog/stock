import json
import requests

from utils import config
from utils import log

DING_ROBOT_URI_TPL = "https://oapi.dingtalk.com/robot/send?access_token={}"


class Ding:
    def __init__(self):
        token = config.get("DING_ROBOT_TOKEN")
        self.url = DING_ROBOT_URI_TPL.format(token)

    def send(self, message):
        '''发送通知'''
        params = {
            "msgtype": "text",
            "text": {
                "content": message,
            },
        }
        resp = requests.post(self.url, json=params)
        result = json.loads(resp.text)
        if result['errcode'] != 0:
            log.error("[ding.send] error: {}".format(resp.text))
