from elasticsearch import Elasticsearch, RequestsHttpConnection

from cpchain.utils import config

es_hosts_string = config.market.es_hosts or '192.168.0.132:9200'
es_hosts = es_hosts_string.split()

es_client = Elasticsearch(
    hosts=es_hosts,
    connection_class=RequestsHttpConnection
)
