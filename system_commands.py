import subprocess


def reboot():
    """
    Reboot the system
    """
    subprocess.run(['sudo', 'reboot'])


def stop_signal_home():
    """
    Stop the service signal-home
    """
    subprocess.run(['sudo', 'systemctl', 'stop', 'signal-home.service'])


def restart_signal_home():
    """
    Restart the service signal-home
    """
    subprocess.run(['sudo', 'systemctl', 'restart', 'signal-home.service'])
