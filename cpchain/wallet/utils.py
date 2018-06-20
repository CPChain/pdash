import urllib.parse


def build_url(url, values):
    data = urllib.parse.urlencode(values)
    new_url = url + "?" + data
    return new_url

def eth_addr_to_string(eth_addr):
    string_addr = eth_addr[2:]
    string_addr = string_addr.lower()
    return string_addr
