from elasticsearch_dsl import DocType, Integer, Text, Keyword, Date, Float


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
    size = Integer()
    username = Text()
    avg_rating = Float()
    sales_number = Integer()

    class Meta:
        index = 'market'

    def save(self, ** kwargs):
        return super().save(**kwargs)
