from elasticsearch import Elasticsearch, RequestsHttpConnection
from elasticsearch_dsl import connections
from cpchain.utils import config

es_hosts_string = config.market.es_hosts or '192.168.0.132:9200'
es_hosts = es_hosts_string.split()

# used by elasticsearch
es_client = Elasticsearch(
    hosts=es_hosts,
    connection_class=RequestsHttpConnection
)
# used by elasticsearch_dsl
connections.configure(
    default={'hosts':es_hosts_string},
)