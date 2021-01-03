import redis


class Redis:
    def __init__(self):
        self.r = redis.StrictRedis(host=config.get("REDIS_HOST"),
                                   prot=config.get("REDIS_PORT"),
                                   db=config.get("REDIS_DB"))
