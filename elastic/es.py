from elasticsearch import Elasticsearch
from elasticsearch import helpers
from dao.dao import Dao
from utils import config

# elasticsearch 索引配置
stock_settings = {
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

# bias index settings
bias_settings = {
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
            "date": {
                "type": "date",
                "format": "yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||epoch_millis"
            },
            "bias": {
                "type": "float"
            }
        }
    }
}

# 索引固定别名
STOCK_ALIAS_INDEX_NAME = "stock"

# bias 索引固定别名
BIAS_ALIAS_INDEX_NAME = "bias"


class ES:
    def __init__(self):
        self.es = Elasticsearch(
            host=config.get("ES_HOST"),
            port=config.get("ES_PORT"),
        )

    def create_index(self, index_name, index_type):
        '''初始化索引'''
        if index_type == 'stock':
            settings = stock_settings
        elif index_type == 'bias':
            settings = bias_settings
        else:
            settings = stock_settings
        return self.es.indices.create(index=index_name, body=settings)

    def bulk_index(self, data):
        '''批量索引数据'''
        if len(data) == 0:
            return None
        return helpers.bulk(self.es, data)

    def create_alias(self, index_name, alias_name):
        '''创建别名'''
        return self.es.indices.put_alias(index=index_name, name=alias_name)

    def get_stock_day_data(self, code, start_date, end_date):
        '''获取个股数据'''
        body = {
            "query": {
                "bool": {
                    "must": [{
                        "term": {
                            "code.keyword": {
                                "value": code,
                            }
                        }
                    }, {
                        "range": {
                            "date": {
                                "gte": start_date,
                                "lte": end_date,
                            }
                        }
                    }]
                }
            },
            "size": 1000,
            "sort": [{
                "date": {
                    "order": "asc"
                }
            }],
            "aggs": {
                "high": {
                    "percentiles": {
                        "field": "high",
                        "percents": [10, 50, 90]
                    }
                },
                "low": {
                    "percentiles": {
                        "field": "low",
                        "percents": [10, 50, 90]
                    }
                },
                "close": {
                    "percentiles": {
                        "field": "close",
                        "percents": [10, 50, 90]
                    }
                }
            }
        }
        return self.es.search(index=STOCK_ALIAS_INDEX_NAME, body=body)

    def remove_stock_data(self, code):
        '''删除个股数据'''
        body = {
            "query": {
                "term": {
                    "code.keyword": code,
                }
            }
        }
        return self.es.delete_by_query(index=STOCK_ALIAS_INDEX_NAME, body=body)
