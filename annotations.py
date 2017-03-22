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
  return __authenticated_handler(original_route_handler, False)

def authenticated_admin(original_route_handler):
  '''Annotates a method such that the user must be logged in and an admin.'''
  return __authenticated_handler(original_route_handler, True)

def __authenticated_handler(original_route_handler, admin):
  @wraps(original_route_handler)
  def new_route_handler(*args, **kwargs):
    if 'reddit_user' not in flask.session or 'name' not in flask.session['reddit_user']:
      return flask.redirect('/')
    elif admin and not ('is_admin' in flask.session and flask.session['is_admin']):
      return flask.redirect('/')
    else:
      return original_route_handler(*args, **kwargs)
  return new_route_handler

def enable_if(enabled):
  '''
  Annotates a route. If enabled, no change to the route. If disabled, all calls
  to the route immediately redirect to root.
  '''
  def wrapper(original_route_handler):
    @wraps(original_route_handler)
    def redirect_to_root():
      return flask.redirect('/')

    if not enabled:
      return redirect_to_root

    return original_route_handler
  return wrapper

redis_store = redis.StrictRedis()
def redis_cache(redis_varname, cache_key_args = [], cache_seconds = 10):
  '''
  Caches return value from the method in the named redis variable.
  '''
  def wrap_redis(uncached_fn):
    @wraps(uncached_fn)
    def cached_fn(*args, **kwargs):
      redis_key = redis_varname
      for cache_key_arg in cache_key_args:
        if cache_key_arg in kwargs:
          redis_key = redis_key + '|' + cache_key_arg + '=' + str(kwargs[cache_key_arg])
      print('using key', redis_key)

      cached_value = redis_store.get(redis_key)
      now = time.time()

      force_refresh = False
      if 'refresh' in kwargs:
        force_refresh = kwargs['refresh']
        del kwargs['refresh']
        if force_refresh:
          print('forcing refresh in call')

      if cached_value is not None and not force_refresh:
        cache_struct = pickle.loads(cached_value)
        if now - cache_struct['cache_time'] < cache_seconds:
          return cache_struct['value']

      return_value = uncached_fn(*args, **kwargs)
      redis_store.set(redis_key, pickle.dumps({
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
