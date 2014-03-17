from functools import wraps
import flask
import pickle
import redis
import time

def authenticated(original_route_handler):
  '''
  Annotates a method such that the user must be logged in to view it.

  Users are returned to the index page if no valid session is present.
  '''
  @wraps(original_route_handler)
  def new_route_handler(*args, **kwargs):
    if 'reddit_user' not in flask.session or 'name' not in flask.session['reddit_user']:
      return flask.redirect('/')
    else:
      return original_route_handler(*args, **kwargs)
  return new_route_handler

redis_store = redis.StrictRedis()
def redis_cache(redis_varname, cache_seconds = 10):
  '''
  Caches return value from the method in the named redis variable.
  '''
  def wrap_redis(uncached_fn):
    @wraps(uncached_fn)
    def cached_fn(*args, **kwargs):
      cached_value = redis_store.get(redis_varname)
      now = time.time()

      if cached_value is not None:
        cache_struct = pickle.loads(cached_value)
        if now - cache_struct['cache_time'] < cache_seconds:
          return cache_struct['value']

      return_value = uncached_fn(*args, **kwargs)
      redis_store.set(redis_varname, pickle.dumps({
        'cache_time': now,
        'value': return_value
      }))
      return return_value

    return cached_fn
  return wrap_redis

def session_cache(session_varname):
  '''
  Caches return value from the method in the named session variable.
  '''
  def wrap(original_route_handler):
    @wraps(original_route_handler)
    def new_route_handler(*args, **kwargs):
      if flask.session.get(session_varname, None) is None:
        return_value = original_route_handler(*args, **kwargs)
        flask.session[session_varname] = return_value

      return flask.session[session_varname]

    return new_route_handler
  return wrap
