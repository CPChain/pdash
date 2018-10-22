
from cpchain.wallet.pages import abs_path

class ProductAdapter:

    def __init__(self, data):
        if isinstance(data, list):
            self.data_ = [self.transform(i) for i in data]
        else:
            self.data_ = self.transform(data)

    @property
    def data(self):
        return self.data_

    def transform(self, data):
        icon_dict = {
            'file': 'icons/icon_batch@2x.png',
            'stream': 'icons/icon_stream@2x.png',
        }
        return dict(image=data['cover_image'] or abs_path('icons/test.png'),
                    icon=abs_path(icon_dict[data['ptype']]),
                    name=data['title'],
                    cpc=data['price'],
                    ptype=data['ptype'],
                    category=data.get('category'),
                    description=data['description'],
                    market_hash=data["msg_hash"],
                    owner_address=data['owner_address'])

    def filter_in(self, key, values):
        results = [i for i in self.data_ if i[key] in values]
        return results
