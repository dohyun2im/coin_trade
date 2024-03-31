import requests

class slack :
    def __init__(self, slack_token, channel) :
        self.token = slack_token
        self.channel = channel

    def message(self, message):
        requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer " + self.token},
        data={"channel": self.channel,"text": message}
    )
