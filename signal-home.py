###############################################################################
#                                                                             #
#   Signal-Home - Bruno Seilliebert                                           #
#                                                                             #
###############################################################################

from freebox_api import FreeboxAPI
import messages
import json
from datetime import datetime, timedelta
import _thread
import websocket
from time import sleep

# Recap messages
START = "Démarrage de Signal-Home"

# Will not send X is back between hour 1 and hour 2
NO_SEND = ["07:00:00", "23:59:59"]

# Time before removing the person from the home
DELTA_BEFORE_REMOVING = 15


class signal_home:
    def __init__(self) -> None:
        self.at_home = []
        self.freeAPI = FreeboxAPI()
        self.date = datetime.now().strftime("%d/%m/%Y")
        self.recap = {}
        # Initialize a family (names, gender, mac adresses, numbers)
        with open('family.json') as file:
            self.family = json.load(file)
        self.macs = {name: self.family[name]["mac"] for name in self.family}
        self.init_at_home()
        self.init_recap()
        messages.AT_HOME = self.at_home
        messages.RECAP = self.recap
        _thread.start_new_thread(self.ws_thread, ())
        _thread.start_new_thread(messages.ws_signal_messages, ())

    def add_to_recap(self, time, msg):
        """
        Add a message to the recap
        """
        if time in self.recap:
            time += datetime.now().strftime(":%S")
        self.recap[time] = msg

    def init_recap(self):
        """
        Initialize the recap
        """
        self.add_to_recap(datetime.now().strftime("%H:%M"), START)

    def check_date(self):
        """
        Check if the date has changed
        """
        if self.date != datetime.now().strftime("%d/%m/%Y"):
            self.date = datetime.now().strftime("%d/%m/%Y")
            messages.BOT.delAllAttachments()
            self.recap = {}
            messages.RECAP = self.recap

    def init_at_home(self):
        """
        Initialize the list of people at home
        """
        r = self.freeAPI.get_devices_connected()
        if r["success"]:
            for device in r["result"]:
                for user in list(self.macs.keys()):
                    if "l3connectivities" in list(device.keys()):
                        if (device["l2ident"]["id"]).lower() in self.macs[user]:
                            if device["reachable"] and device["active"]:
                                member = self.family[user]
                                name = member.get('name')
                                if name not in self.at_home:
                                    self.at_home.append(name)
        else:
            assert False, "Error while getting devices connected"

    def check_if_at_home(self, name):
        """
        Check if a person is at home
        """
        api = FreeboxAPI()
        r = api.get_devices_connected()
        mac = self.macs[name]
        if r["success"]:
            for device in r["result"]:
                if "l3connectivities" in list(device.keys()):
                    if (device["l2ident"]["id"]).lower() in mac:
                        if device["reachable"] and device["active"]:
                            return True
        return False

    def add_at_home(self, name):
        """
        Add a person to the list of people at home
        """
        if name not in self.at_home:
            if 'left_time' in self.family[name]:
                del self.family[name]['left_time']
            self.at_home.append(name)
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            self.add_to_recap(now.strftime("%H:%M"),
                              messages.IS_BACK[self.family[name]['gender']][0].format(name))
            if NO_SEND[0] < current_time < NO_SEND[1]:
                messages.send_is_back(name)

    def remove_at_home(self, name):
        """
        Remove a person from the list of people at home
        """
        if name in self.at_home:
            if 'left_time' in self.family[name]:
                left_time = self.family[name]['left_time']
                updated_time = (
                    left_time + timedelta(minutes=DELTA_BEFORE_REMOVING))
                current_time = datetime.now()

                if current_time > updated_time:
                    if self.check_if_at_home(name):
                        del self.family[name]['left_time']
                    else:
                        self.at_home.remove(name)
                        self.add_to_recap(left_time.strftime("%H:%M"),
                                          messages.IS_AWAY[self.family[name]['gender']][0].format(name))
                        del self.family[name]['left_time']
            else:
                self.before_removing(name)

    def before_removing(self, name):
        """
        Update the time when a person left home
        """
        if name in self.at_home and 'left_time' not in self.family[name]:
            self.family[name]['left_time'] = datetime.now()

    def on_open(self, ws):
        to_send = {"RegisterAction": {"action": "register",
                                      "events": ["lan_host_l3addr_reachable"]}}
        to_send = {
            "request_id": 1,
            "action": "register",
            "events": ["lan_host_l3addr_reachable", "lan_host_l3addr_unreachable"]
        }
        ws.send(json.dumps(to_send))

    def on_error(self, ws, error):
        print("error : " + str(error))

    def ws_message(self, ws,  message):
        """
        Message received from the websocket
        """
        res = json.loads(message)
        if not res["success"]:
            assert False, "Error in websocket freebox"
        if "action" in list(res.keys()) and res["action"] == "register":
            messages.send_connection_established()
        else:
            print(res)
            for user in list(self.macs.keys()):
                if "l3connectivities" in list(res["result"].keys()):
                    if (res["result"]["l2ident"]["id"]).lower() in self.macs[user]:
                        if res["result"]["reachable"] and res["result"]["active"]:
                            member = self.family[user]
                            self.add_at_home(member.get('name'))
                        else:
                            member = self.family[user]
                            if not self.check_if_at_home(member.get('name')):
                                self.remove_at_home(member.get('name'))

    def ws_thread(self):
        """
        Thread to listen to the websocket
        """
        header = {'X-Fbx-App-Auth': self.freeAPI.session_token}
        ws = websocket.WebSocketApp(self.freeAPI.ws_url,
                                    on_open=self.on_open,
                                    on_message=self.ws_message,
                                    on_error=self.on_error,
                                    header=header)
        ws.run_forever()


def wait_for_signal_cli():
    while not messages.BOT.is_alive():
        continue


def main():
    """
    Main function
    """
    wait_for_signal_cli()
    s = signal_home()
    while True:
        sleep(1)
        s.check_date()
        for person in s.family:
            if 'left_time' in s.family[person]:
                s.remove_at_home(person)


if __name__ == "__main__":
    main()
