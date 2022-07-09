# signal-home
![image](https://user-images.githubusercontent.com/77984019/178110168-7e6bafbf-0b12-4ec2-b52e-d6e34cfbf2c2.png)

signal-home is a script sending a message to a signal group when someone of your family connects to wifi (freebox)

## How does it works?

It uses two main APIs:
- freebox API: present on the freebox (French modem)
- [signal-cli-rest-api](https://github.com/bbernhard/signal-cli-rest-api)

It's running on a Raspberry Pi 3 with systemd

When someone connects to the wifi, the websocket of the freebox API sends a signal to the script which checks if the new device connected is one of the [family](family.json). If it does, the script sends a message to the chosen Signal group through the signal-cli-rest-api running on the Pi too.

The script handles commands too:
- -home: it sends who are at home
- -stop: to stop the execution of the script
- -recap: to get the summary of what happened in the day
- -help: to get the list of commands

When someone of the [family](family.json) or someone on the group send one of the commands, the script will respond to it.
