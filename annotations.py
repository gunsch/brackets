from functools import wraps
import flask

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
