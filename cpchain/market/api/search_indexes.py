from elasticsearch_dsl import DocType, Integer, Text, Keyword, Date


class ProductIndex(DocType):
    """
    The product model.
    """
    owner_address = Text()
    title = Text(fields={'raw': Keyword()})
    description = Text()
    tags = Keyword(multi=True)
    price = Text()
    created = Date()
    start_date = Date()
    end_date = Date()
    status = Integer()
    msg_hash = Keyword()

    class Meta:
        index = 'market'

    def save(self, ** kwargs):
        return super().save(**kwargs)
