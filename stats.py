from collections import defaultdict
from functools import wraps
import flask

__GLOBAL_STATS_COUNTER = defaultdict(int);
__GLOBAL_STATS_INSTANCE = None
def __GLOBAL_STATS_ROUTE():
  return flask.Response(
      '\n'.join(sorted(
          ['%s=%s' % (name, value) for (name, value) in __GLOBAL_STATS_COUNTER.iteritems()])),
      mimetype = 'text/plain')

def record_one(action):
  __GLOBAL_STATS_COUNTER[action] = __GLOBAL_STATS_COUNTER[action] + 1

def record(prefix = None):
  def wrapper(fn):
    @wraps(fn)
    def recording_fn(*args, **kwargs):
      if prefix is not None:
        record_one('%s.%s' % (prefix, fn.__name__))
      else:
        record_one(fn.__name__)
      return fn(*args, **kwargs)
    return recording_fn
  return wrapper

def Stats(app):
  app.route("/varz")(__GLOBAL_STATS_ROUTE)
