from elasticsearch import Elasticsearch
from elasticsearch import helpers
from dao.dao import Dao
from utils import config

# elasticsearch 索引配置
settings = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 3
    },
    "mappings": {
        "properties": {
            "code": {
                "type": "text",
                "fields": {
                    "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                    }
                }
            },
            "open": {
                "type": "float"
            },
            "high": {
                "type": "float"
            },
            "low": {
                "type": "float"
            },
            "close": {
                "type": "float"
            },
            "preclose": {
                "type": "float"
            },
            "volume": {
                "type": "long"
            },
            "amount": {
                "type": "float"
            },
            "turn": {
                "type": "float"
            },
            "pe_ttm": {
                "type": "float"
            },
            "date": {
                "type": "date",
                "format": "yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||epoch_millis"
            }
        }
    }
}

# 索引固定别名
STOCK_ALIAS_INDEX_NAME = "stock"


class ES:
    def __init__(self):
        self.es = Elasticsearch(
            host=config.get("ES_HOST"),
            port=config.get("ES_PORT"),
        )

    def create_index(self, index_name):
        '''初始化索引'''
        return self.es.indices.create(index=index_name, body=settings)

    def bulk_index(self, data):
        '''批量索引数据'''
        if len(data) == 0:
            return None
        return helpers.bulk(self.es, data)

    def create_alias(self, index_name):
        '''创建别名'''
        return self.es.indices.put_alias(index=index_name,
                                         name=STOCK_ALIAS_INDEX_NAME)
