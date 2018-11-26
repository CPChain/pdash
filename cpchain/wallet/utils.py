import glob
import time
import urllib.parse
import os
from datetime import datetime as dt

import qrcode
from cpchain.crypto import ECCipher, Encoder
from cpchain.utils import config, root_dir


def get_cpc_free_qrcode():
    path = os.path.expanduser('~/.cpchain') + '/tmp_cpc_free.png'
    if os.path.exists(path):
        return path
    data = config.account.charge_server
    qr = qrcode.QRCode(
        version=1,
        # 4 level: L, M, Q, H
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=1,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image()
    img.save(path)
    return path


def build_url(url, values):
    if values:
        if 'timestamp' not in values:
            values['timestamp'] = str(time.time())
    else:
        values = dict(timestamp=str(time.time()))
    data = urllib.parse.urlencode(query=values, quote_via=urllib.parse.quote)
    new_url = url + "?" + data
    return new_url

def eth_addr_to_string(eth_addr):
    string_addr = eth_addr[2:]
    string_addr = string_addr.lower()
    return string_addr

def get_address_from_public_key_object(pub_key_string):
    pub_key = get_public_key(pub_key_string)
    return ECCipher.get_address_from_public_key(pub_key)

def get_public_key(public_key_string):
    pub_key_bytes = Encoder.hex_to_bytes(public_key_string)
    return ECCipher.create_public_key(pub_key_bytes)

def formatTimestamp(timestamp):
    months = [
        ["Jan.", "January"],
        ["Feb.", "February"],
        ["Mar.", "March"],
        ["Apr.", "April"],
        ["May", "May"],
        ["Jun.", "June"],
        ["Jul.", "July"],
        ["Aug.", "August"],
        ["Sept.", "September"],
        ["Oct.", "October"],
        ["Nov.", "November"],
        ["Dec.", "December"],
    ]
    return months[timestamp.month - 1][0] + ' ' + timestamp.strftime('%d, %Y')

def to_datetime(created):
    return dt.strptime(created, '%Y-%m-%dT%H:%M:%SZ')

def load_fonts(path):
    # load fonts
    from PyQt5.QtGui import QGuiApplication, QFontDatabase, QFont
    for font in glob.glob('{}/*'.format(path)):
        font_id = QFontDatabase.addApplicationFont(font)

def _handle_keyboard_interrupt():
    def sigint_handler(*_):
        # _Application.quit()
        pass

    import signal
    signal.signal(signal.SIGINT, sigint_handler)

    from PyQt5.QtCore import QTimer

    _handle_keyboard_interrupt.timer = QTimer()
    timer = _handle_keyboard_interrupt.timer
    timer.start(300)
    timer.timeout.connect(lambda: None)
