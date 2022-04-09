###############################################################################
#                                                                             #
# Definition of the Freebox API with useful functions to connect to the API   #
# and to get informations about devices connected.                            #
#                                                                             #
###############################################################################
import json
from time import sleep
import requests
import hmac


# Initialize application name for the freebox
DEFAULT = {
    "app_id": "signal-home",
    "app_name": "signal_home",
    "app_version": "4.0.1",
    "device_name": "signal-home"
}


class FreeboxAPI:
    def __init__(self) -> None:
        """
        Initialize FreeboxAPI
        """
        self.url = 'http://mafreebox.freebox.fr'
        self.ws_url = 'ws://mafreebox.freebox.fr/api/v8/ws/event'
        self.app_token, self.track_id = self.get_app_token()
        self.challenge = self.get_challenge(self.track_id)
        self.app_id = DEFAULT["app_id"]
        self.session_token = self.get_session_token(
            self.app_token, self.challenge)

    def __repr__(self) -> str:
        """
        Return a string representation of the object
        """
        return 'FreeboxAPI()'

    def get_app_token(self):
        """
        Get the app token
        """
        data = json.dumps(DEFAULT)
        try:
            with open("token.json") as f:
                r = json.load(f)
        except:
            r = requests.post(self.url + "/api/v8/login/authorize/", data)
            r = r.json()
            print("Accept message on the freebox (wait 120s)")
            sleep(120)
            with open("token.json", "w") as f:
                json.dump(r, f)
        return r["result"]["app_token"], r["result"]["track_id"]

    def get_challenge(self, track_id):
        """
        Get the challenge

        :param url: url of the freebox
        :param track_id: track id of the application
        """
        url = self.url + "/api/v8/login/authorize/" + str(track_id)
        r = requests.get(url)
        r.encoding = "utf-8"
        r = r.json()
        if r["success"]:
            return r["result"]["challenge"]
        return "ERROR"

    def get_session_token(self, app_token, challenge):
        """
        Get the session token
        """
        h = hmac.new(app_token.encode(), challenge.encode(), 'sha1')
        password = h.hexdigest()
        data = json.dumps({'app_id': self.app_id, 'password': password})
        url = self.url + "/api/v8/login/session/"
        r = requests.post(url, data, timeout=10)
        r = r.json()
        if r["success"]:
            return r["result"]["session_token"]
        return "ERROR"

    def get_devices_connected(self):
        """
        Get the devices connected
        """
        header = {'X-Fbx-App-Auth': self.session_token}
        r = requests.get(
            self.url + "/api/v8/lan/browser/pub/", headers=header)
        return r.json()
