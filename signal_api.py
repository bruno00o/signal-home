###############################################################################
#                                                                             #
#   SignalBot : class to use the Signal Cli Rest API                          #
#   https://github.com/bbernhard/signal-cli-rest-api                          #
#                                                                             #
###############################################################################

import requests
import json


class SignalBot:
    def __init__(self, url, num):
        """
        Initialize SignalBot

        :param url: url of the Signal Cli Rest API
        :param num: telephone number used with the API
        """
        if url[-1] != '/':
            url += '/'
        self.url = url
        self.num = num

    def __repr__(self) -> str:
        """
        Return a string representation of the object
        """
        return 'SignalBot(' + str(self.num) + ')'

    def __str__(self) -> str:
        about = 'v1/about'
        r = requests.get(self.url + about)
        r = json.loads(r.text)
        string = 'num : ' + str(self.num) + '\n' + \
            'url : ' + str(self.url) + '\n' + \
            'versions : ' + str(r["versions"]) + '\n' + \
            'build : ' + str(r["build"]) + '\n' + \
            'mode : ' + str(r["mode"])
        return string

    def is_alive(self):
        return requests.get(self.url + 'v1/about')

    def listGroups(self):
        """
        List all groups of the given number

        :return: list of groups (list of dict)
        """
        listgroups = 'v1/groups/' + self.num
        r = requests.get(self.url + listgroups)
        r = json.loads(r.text)
        return r

    def send(self, message, recipients):
        """
        Send a message to the given recipients

        :param message: message to send
        :param recipients: list of recipients
        """
        if type(recipients) != list:
            recipients = [recipients]
        send = 'v2/send'
        payload = {
            "message": message,
            "number": self.num,
            "recipients": recipients
        }
        r = requests.post(self.url + send, data=json.dumps(payload))
        return r.text

    def addReaction(self, reaction, recipient, target, timestamp):
        """
        Add a reaction to a message

        :param reaction: reaction to add
        :param recipient: recipient for the reaction
        :param target: target author
        :param timestamp: timestamp of the message to react to
        """
        reac = 'v1/reactions/' + self.num
        payload = {
            "reaction": reaction,
            "recipient": recipient,
            "target_author": target,
            "timestamp": timestamp
        }
        r = requests.post(self.url + reac, data=json.dumps(payload))
        return r.text

    def listAttachments(self):
        """
        List all attachments of the given number

        :return: list of attachments
        """
        listAttachments = 'v1/attachments'
        r = requests.get(self.url + listAttachments)
        r = json.loads(r.text)
        return r

    def deleteAttachment(self, att):
        """
        Delete an attachment

        :param att: attachment to delete
        """
        delete = 'v1/attachments/' + att
        requests.delete(self.url + delete)

    def delAllAttachments(self):
        """
        Delete all attachments of the given number
        """
        for att in self.listAttachments():
            self.deleteAttachment(att)
