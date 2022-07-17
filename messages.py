###############################################################################
#                                                                             #
#   Signal-Home messages                                                      #
#                                                                             #
###############################################################################

import json
from signal_api import SignalBot
from random import choice
import websocket
import system_commands
from datetime import datetime


SIGNAL_CLI = "http://localhost:8080/"
WS_SIGNAL_CLI = "ws://localhost:8080/"

# Initialize SignalBot
BOT_PHONE_NUMBER = "+33600000000"
BOT = SignalBot(SIGNAL_CLI, BOT_PHONE_NUMBER)

AT_HOME = []
RECAP = {}
MUTE = False
UNMUTE_HOUR = "20:00:00"

# Initialize variables of Groups (this will send messages to this group)
GROUP = ''
GROUP_ID = ''

# Command key to put in Signal messages to send commands
COMMAND_KEY = '-'

# Keywords

AT_HOME_KW = ['maison', 'home', 'qui est à la maison', 'qui est à la maison?']
STOP_KW = ['stop']
REBOOT_KW = ['reboot', 'redémarrer']
HELP_KW = ['help', 'aide']
THANKS_KW = ['merci', 'thanks', 'thank you', 'thank you very much']
RECAP_KW = ['recap', 'récap', 'récapitulatif']
MUTE_KW = ['mute', 'silence', 'silencez']
UNMUTE_KW = ['unmute']

# Initialize a family (names, gender, mac adresses, numbers)
with open('family.json') as file:
    FAMILY = json.load(file)

# Initialize list of numbers in family
NUMBERS = [FAMILY[i]["tel"] for i in FAMILY]
ADMIN_NAME = "admin"
ADMIN = FAMILY[ADMIN_NAME]["tel"]

# Messages

COMMANDS = ["maison", "stop", "aide", "recap", "mute", "unmute"]
EMOJIS = ["👍", "👏", "🙌", "🆗", "✅", "👌", "🙆"]
IS_BACK = {'M': ["{} est rentré", "{} est rentré !", "{} est rentré 🏠", "{} 🔙 🏡"],
           'F': ["{} est rentrée", "{} est rentrée !", "{} est rentrée 🏠", "{} 🔙 🏡"]}
IS_AWAY = {'M': ["{} est parti"], 'F': ["{} est partie"]}
AT_HOME_MSG = {0: ["Personne n'est à la maison",
                   "Il n'y a personne à la maison",
                   "Personne n'est à la maison 😔"],
               1: ["{} est à la maison", "{} is at home 🏠"],
               "X": ["{} {} {} sont à la maison",
                     "sont à la maison : {} {} {}",
                     "{} {} {} sont à la maison !",
                     "{} {} {} sont à la maison 🏠"],
               len(FAMILY): ["Tout le monde est à la maison",
               "Il y a tout le monde à la maison",
                             "Tout le monde est à la maison 🏠"]}
HELP_MSG = {"list": "Liste des commandes : \n- ",
            "key": "Une commande doit commencer par le caractère '{}'".format(COMMAND_KEY)}
YOUR_WELCOME_MSG = ["Pas de soucis !", "Pas de problème", "👍"]
MUTE_MSG = ["La maison passe en silencieuse", "Je ne fais plus aucun bruit 🤫"]
MUTE_PEOPLE_MSG = ["{} passe en silencieux",
                   "Vous ne serez pas si {} est de retour"]
UNMUTE_MSG = ["La maison n'est plus silencieuse", "Je peux reparler 🗣️"]
ERROR_MEMBER = ["{} n'est pas dans ma famille"]
UNMUTE_PEOPLE_MSG = ["{} n'est plus silencieux"]
STOP_MSG = "Signal-Home va s'arrêter"
REBOOT_MSG = "Signal-Home va redémarrer"
AND = "et"
CONNECTION_ESTABLISHED = "Connection Freebox établie !"
EMPTY_RECAP = ["Rien à signaler aujourd'hui !",
               "Il ne s'est encore rien passé 👀"]

# Reactions

ON_THE_WAY = ["on rentre", "je rentre"]
ARRIVED = ["je suis arrivé", "je suis au bureau", "je suis à la maison",
           "je suis arrivée"]
ASKED_AT_HOME = ["qui est à la maison", "qui est à la maison?", "qui est à la maison ?",
                 "y a qui à la maison", "y a qui à la maison ?", "y a quelqu'un à la maison"]

# Functions


def send_is_back(name):
    """
    Send signal message to the group to say a person is back home

    :param name: string name of the person back
    """
    if MUTE is True and datetime.now().strftime("%H:%M:%S") > UNMUTE_HOUR:
        MUTE = False
    if MUTE is False:
        if "MUTE" in FAMILY[name]:
            if FAMILY[name]["MUTE"] is False:
                BOT.send(choice(IS_BACK[FAMILY[name]["gender"]]
                                ).format(name), GROUP_ID)
        else:
            BOT.send(choice(IS_BACK[FAMILY[name]["gender"]]
                            ).format(name), GROUP_ID)


def send_is_away(name):
    """
    Send signal message to the group to say a person is leaving

    :param name: string name of the person leaving
    """
    if MUTE is True and datetime.now().strftime("%H:%M:%S") > UNMUTE_HOUR:
        MUTE = False
    if MUTE is False:
        if "MUTE" in FAMILY[name]:
            if FAMILY[name]["MUTE"] is False:
                BOT.send(choice(IS_AWAY[FAMILY[name]["gender"]]
                                ).format(name), GROUP_ID)
        else:
            BOT.send(choice(IS_AWAY[FAMILY[name]["gender"]]
                            ).format(name), GROUP_ID)


def send_at_home(sender):
    """
    Send who is at home

    :param sender: string sender of the message
    """
    if len(AT_HOME) == 0:
        msg = choice(AT_HOME_MSG[0])
    elif len(AT_HOME) == 1:
        msg = choice(AT_HOME_MSG[1]).format(AT_HOME[0])
    elif len(AT_HOME) == len(FAMILY):
        msg = choice(AT_HOME_MSG[len(FAMILY)])
    else:
        msg = choice(AT_HOME_MSG["X"]).format(
            ", ".join(AT_HOME[:-1]), AND, AT_HOME[-1])
    BOT.send(msg, sender)


def send_recap(sender):
    """
    Send recap message

    :param sender: string sender of the message
    """
    if RECAP != {}:
        msg = ""
        for hour in RECAP:
            msg += "{} : {}\n".format(hour, RECAP[hour])
        BOT.send(msg, sender)
    else:
        BOT.send(choice(EMPTY_RECAP), sender)


def send_help(sender):
    """
    Send help message

    :param sender: string sender of the message
    """
    msg = HELP_MSG["list"]
    msg += "\n- ".join(COMMANDS)
    msg += "\n\n" + HELP_MSG["key"]
    BOT.send(msg, sender)


def send_your_welcome(sender):
    """
    Send welcome message

    :param sender: string sender of the message
    """
    BOT.send(choice(YOUR_WELCOME_MSG), sender)


def check_sender(group, src):
    if group == None and src in NUMBERS:
        sender = src
    elif group == GROUP:
        sender = GROUP_ID
    return sender


def mute(message, sender):
    """
    Mute the bot

    :param message: string message sent by the bot
    """
    if " " in message:
        message = message.split(" ")
    else:
        message = [message]
    if message[0][1:] in MUTE_KW:
        if len(message) == 1:
            BOT.send(choice(MUTE_MSG), sender)
            MUTE = True
        elif len(message) >= 2:
            if message[1][0].upper() + message[1][1:].lower() in FAMILY:
                FAMILY[message[1][0].upper() + message[1][1:].lower()
                       ]["mute"] = True
                BOT.send(choice(MUTE_PEOPLE_MSG).format(
                    message[1][0].upper() + message[1][1:].lower()), sender)
            else:
                BOT.send(choice(ERROR_MEMBER).format(
                    message[1][0].upper() + message[1][1:].lower()), sender)


def unmute(message, sender):
    """
    Unmute the bot

    :param message: string message sent by the bot
    """
    if " " in message:
        message = message.split(" ")
    else:
        message = [message]
    if message[0][1:] in UNMUTE_KW:
        if len(message) == 1:
            BOT.send(choice(UNMUTE_MSG), sender)
            MUTE = False
        elif len(message) >= 2:
            if message[1][0].upper() + message[1][1:].lower() in FAMILY:
                FAMILY[message[1][0].upper() + message[1][1:].lower()
                       ]["mute"] = False
                BOT.send(choice(UNMUTE_PEOPLE_MSG).format(
                    message[1][0].upper() + message[1][1:].lower()), sender)
            else:
                BOT.send(choice(ERROR_MEMBER).format(
                    message[1][0].upper() + message[1][1:].lower()), sender)


def check_command(src, message, group):
    """
    Check commands and react to them

    :param src: string sender of the message
    :param message: string message
    :param group: string group id
    :param ts: int timestamp of the message
    """
    sender = check_sender(group, src)
    command = message[1:].lower().strip()
    if command in AT_HOME_KW:
        send_at_home(sender)
    elif command in STOP_KW:
        BOT.send(STOP_MSG, sender)
        system_commands.stop_signal_home()
    elif command in REBOOT_KW:
        BOT.send(REBOOT_MSG, sender)
        system_commands.reboot()
    elif command in HELP_KW:
        send_help(sender)
    elif command in THANKS_KW:
        send_your_welcome(sender)
    elif command in RECAP_KW:
        send_recap(sender)
    elif command in MUTE_KW:
        mute(message, sender)
    elif command in UNMUTE_KW:
        unmute(message, sender)
    else:
        if " " in command:
            command = command.split(" ")
            if command[0] in MUTE_KW:
                mute(message, sender)
            elif command[0] in UNMUTE_KW:
                unmute(message, sender)


def check_message(src, message, group, ts):
    """
    Check if the message is a command or a message to react to

    :param src: string sender of the message
    :param message: string message
    :param group: string group id
    :param ts: int timestamp of the message
    """
    if message.startswith(COMMAND_KEY):
        check_command(src, message, group)
    elif group == GROUP:
        message = message.lower().strip()
        if message in ON_THE_WAY or message in ARRIVED:
            BOT.addReaction(choice(EMOJIS), GROUP_ID, src, ts)
        elif message in ASKED_AT_HOME:
            sender = check_sender(group, src)
            send_at_home(sender)


def ws_on_message(ws, message):
    """
    Callback function for the websocket

    :param ws: websocket
    :param message: string message
    """
    data = json.loads(message)
    src = data["envelope"]["source"]
    message = data["envelope"]["dataMessage"]["message"]
    try:
        group = data["envelope"]["dataMessage"]["groupInfo"]["groupId"]
    except:
        group = None
    ts = data["envelope"]["dataMessage"]["timestamp"]
    check_message(src, message, group, ts)


def ws_signal_messages():
    """
    Connect to the websocket and listen to messages
    """
    url = WS_SIGNAL_CLI + "v1/receive/" + BOT.num
    ws = websocket.WebSocketApp(url, on_message=ws_on_message)
    ws.run_forever()


def send_connection_established():
    """
    Send a message to the group to say the bot is connected
    """
    BOT.send(CONNECTION_ESTABLISHED, ADMIN)
