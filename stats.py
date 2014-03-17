from collections import defaultdict
from functools import wraps
import flask
import time

__GLOBAL_STATS_COUNTER = defaultdict(int);
__GLOBAL_STATS_INSTANCE = None

def __GLOBAL_STATS_ROUTE():
  text = []
  for (name, value) in __GLOBAL_STATS_COUNTER.iteritems():
    if type(value) is list:
      value = float(sum(value)) / len(value)
    text.append('%s=%s' % (name, value))
  return flask.Response('\n'.join(sorted(text)), mimetype = 'text/plain')

def record_one(action):
  __GLOBAL_STATS_COUNTER[action] = __GLOBAL_STATS_COUNTER[action] + 1

def record(prefix = None, timing = False):
  def wrapper(fn):
    @wraps(fn)
    def recording_fn(*args, **kwargs):
      record_name = (
            '%s.%s' % (prefix, fn.__name__)
            if prefix is not None else
            fn.__name__)
      record_one(record_name)

      if not timing:
        return fn(*args, **kwargs)

      starttime = time.time()
      result = fn(*args, **kwargs)
      endtime = time.time()

      timing_name = record_name + '_ms'
      if timing_name not in __GLOBAL_STATS_COUNTER:
        __GLOBAL_STATS_COUNTER[timing_name] = []
      __GLOBAL_STATS_COUNTER[timing_name].append((endtime - starttime) * 1000.0)

      return result

    return recording_fn
  return wrapper

def Stats(app):
  app.route("/varz")(__GLOBAL_STATS_ROUTE)
