
# Lazy, static hack to get a global instance of this thing.
# I'm adding this in the process of Dockerizing things and it's just not the
# problem I want to solve right now.
redis_instance = None
def get_redis_HACK(callback = None):
    global redis_instance
    if redis_instance is None:
        if callback is None:
            raise Exception('redis_instance not yet created')
        redis_instance = callback()
    return redis_instance
