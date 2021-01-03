import json
import requests

from utils import config
from utils import log


class Ding:
    def __init__(self):
        self.token = config.get("DING_ROBOT_TOKEN")
        self.url = "https://oapi.dingtalk.com/robot/send?access_token={}".format(
            self.token)
        self.message_template = '''[ALERT] {}'''

    def send(self, message):
        '''发送通知'''
        content = self.message_template.format(message)
        params = {
            "msgtype": "text",
            "text": {
                "content": content,
            },
        }
        resp = requests.post(self.url, json=params)
        result = json.loads(resp.text)
        if result['errcode'] != 0:
            log.error("[ding.send] error: {}".format(resp.text))
