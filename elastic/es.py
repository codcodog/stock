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

# fund index settings
fund_settings = {
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
            "price": {
                "type": "float"
            }
        }
    }
}

# 索引固定别名
STOCK_ALIAS_INDEX_NAME = "stock"

# 基金索引固定名
FUND_ALIAS_INDEX_NAME = "fund"

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
        elif index_type == 'fund':
            settings = fund_settings
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
                        "percents": [80]
                    }
                },
                "low": {
                    "percentiles": {
                        "field": "low",
                        "percents": [5]
                    }
                },
                "close": {
                    "percentiles": {
                        "field": "close",
                        "percents": [50]
                    }
                }
            }
        }
        return self.es.search(index=STOCK_ALIAS_INDEX_NAME, body=body)

    def get_fund_day_data(self, code, start_date, end_date):
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
                "price": {
                    "percentiles": {
                        "field": "price",
                        "percents": [20, 50, 80]
                    }
                }
            }
        }
        return self.es.search(index=FUND_ALIAS_INDEX_NAME, body=body)

    def remove_stock_data(self, code):
        '''删除个股数据'''
        body = {
            "query": {
                "term": {
                    "code.keyword": code,
                }
            }
        }
        self.es.delete_by_query(index=STOCK_ALIAS_INDEX_NAME, body=body)
        self.es.delete_by_query(index=FUND_ALIAS_INDEX_NAME, body=body)
        self.es.delete_by_query(index=BIAS_ALIAS_INDEX_NAME, body=body)

    def incr_index_bias(self, code, date, bias):
        '''增量索引 bias 数据'''
        bias_data = {
            '_index': BIAS_ALIAS_INDEX_NAME,
            '_source': {
                'code': code,
                'date': date,
                'bias': bias,
            }
        }
        data = [bias_data]
        return self.bulk_index(data)

    def get_bias_data(self, code, start_date, end_date):
        '''获取某股 bias 数据'''
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
                "bias": {
                    "percentiles": {
                        "field": "bias",
                        "percents": [5, 50, 80]
                    }
                }
            }
        }
        return self.es.search(index=BIAS_ALIAS_INDEX_NAME, body=body)
