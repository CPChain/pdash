import urllib.parse


def build_url(url, values):
    data = urllib.parse.urlencode(values)
    new_url = url + "?" + data
    return new_url
