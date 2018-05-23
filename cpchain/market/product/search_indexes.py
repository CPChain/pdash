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

    username = Text()
    avg_rating = Float()
    sales_number = Integer()

    # p['username'] = '' if not u else u.username
    # # query average rating from SummaryComment table
    # comment, _ = SummaryComment.objects.get_or_create(market_hash=p['msg_hash'])
    # sale_status, _ = ProductSaleStatus.objects.get_or_create(market_hash=p['msg_hash'])
    # p['avg_rating'] = 1 if not comment else comment.avg_rating
    # p['sales_number'] = 0 if not sale_status else sale_status.sales_number

    class Meta:
        index = 'market'

    def save(self, ** kwargs):
        return super().save(**kwargs)
