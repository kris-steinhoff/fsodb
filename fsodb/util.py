# -*- encoding: UTF-8 -*-
#
# Form based authentication for CherryPy. Requires the
# Session tool to be loaded.
#

import cherrypy

SESSION_KEY = '_cp_username'

def check_credentials(username, password):
    """Verifies credentials for username and password.
    Returns None on success or a string describing the error on failure"""
    # Adapt to your needs
    if username in ('joe', 'steve') and password == 'secret':
        return None
    else:
        return u"Incorrect username or password."
    
    # An example implementation which uses an ORM could be:
    # u = User.get(username)
    # if u is None:
    #     return u"Username %s is unknown to me." % username
    # if u.password != md5.new(password).hexdigest():
    #     return u"Incorrect password"

def check_auth(*args, **kwargs):
    """A tool that looks in config for 'auth.require'. If found and it
    is not None, a login is required and the entry is evaluated as a list of
    conditions that the user must fulfill"""
    conditions = cherrypy.request.config.get('auth.require', None)
    if conditions is not None:
        username = cherrypy.session.get(SESSION_KEY)
        if username:
            cherrypy.request.login = username
            for condition in conditions:
                # A condition is just a callable that returns true or false
                if not condition():
                    raise cherrypy.HTTPRedirect("/auth/login")
        else:
            raise cherrypy.HTTPRedirect("/auth/login")
    
cherrypy.tools.auth = cherrypy.Tool('before_handler', check_auth)

def require(*conditions):
    """A decorator that appends conditions to the auth.require config
    variable."""
    def decorate(f):
        if not hasattr(f, '_cp_config'):
            f._cp_config = dict()
        if 'auth.require' not in f._cp_config:
            f._cp_config['auth.require'] = []
        f._cp_config['auth.require'].extend(conditions)
        return f
    return decorate


# Conditions are callables that return True
# if the user fulfills the conditions they define, False otherwise
#
# They can access the current username as cherrypy.request.login
#
# Define those at will however suits the application.

def member_of(groupname):
    def check():
        # replace with actual check if <username> is in <groupname>
        return cherrypy.request.login == 'joe' and groupname == 'admin'
    return check

def name_is(reqd_username):
    return lambda: reqd_username == cherrypy.request.login

# These might be handy

def any_of(*conditions):
    """Returns True if any of the conditions match"""
    def check():
        for c in conditions:
            if c():
                return True
        return False
    return check

# By default all conditions are required, but this might still be
# needed if you want to use it inside of an any_of(...) condition
def all_of(*conditions):
    """Returns True if all of the conditions match"""
    def check():
        for c in conditions:
            if not c():
                return False
        return True
    return check


# Controller to provide login and logout actions

class AuthController(object):
    
    def on_login(self, username):
        """Called on successful login"""
    
    def on_logout(self, username):
        """Called on logout"""
    
    def get_loginform(self, username, msg="Enter login information", from_page="/"):
        return """<html><body>
            <form method="post" action="/auth/login">
            <input type="hidden" name="from_page" value="%(from_page)s" />
            %(msg)s<br />
            Username: <input type="text" name="username" value="%(username)s" /><br />
            Password: <input type="password" name="password" /><br />
            <input type="submit" value="Log in" />
        </body></html>""" % locals()
    
    @cherrypy.expose
    def login(self, username=None, password=None, from_page="/"):
        if username is None or password is None:
            return self.get_loginform("", from_page=from_page)
        
        error_msg = check_credentials(username, password)
        if error_msg:
            return self.get_loginform(username, error_msg, from_page)
        else:
            cherrypy.session[SESSION_KEY] = cherrypy.request.login = username
            self.on_login(username)
            raise cherrypy.HTTPRedirect(from_page or "/")
    
    @cherrypy.expose
    def logout(self, from_page="/"):
        sess = cherrypy.session
        username = sess.get(SESSION_KEY, None)
        sess[SESSION_KEY] = None
        if username:
            cherrypy.request.login = None
            self.on_logout(username)
        raise cherrypy.HTTPRedirect(from_page or "/")

def get_auth():
    userpassdict = {'kris@ofa2.com' : '12345', 'andrew@moretension.com' : '12345'}
    checkpassword = cherrypy.lib.auth_basic.checkpassword_dict(userpassdict)
    basic_auth = {'tools.auth_basic.on': True,
                  'tools.auth_basic.realm': 'earth',
                  'tools.auth_basic.checkpassword': checkpassword,
                 }
    return basic_auth


class Import(object):
    exposed = True

    def GET(self):
        return """
        <html><body>
            <form action="" method="post" enctype="multipart/form-data">
            <input type="file" name="myFile" /><br />
            <input type="submit" value="Import" />
            </form>
        </body></html>
        """

    def POST(self, myFile):
        out = """
<html>
    <head>
        <style>
            .entry {
                font-family: monospace;
                width: 100%;
                border: 1px solid black;
                margin-bottom: 5px;
                padding: 6px;
            }
            .header {
                font-weight: bold;
                font-size: 110%;
            }
            .subheader {
                color: #444;
                font-size: 80%;
            }
            pre {
                padding: 0;
                margin: 0;
        </style>
    </head>
    <body>
"""
        template = """
        <div class="entry" title="{lines}">
            <div class="header">{path}</div>
            <div class="subheader">{line}</div>
            <pre>{comment}</pre>
        </div>
"""
        comment = ""
        lines = ""
        c = cherrypy.thread_data.db.cursor()
        try:
            while True:

                line = myFile.file.readline()
                if not line:
                    break

                if len(line.strip()) == 0:
                    continue

                lines += line

                if line.strip()[0:1] == "#":
                    comment += line.strip()[1:].strip() + "\n"
                    continue

                line_parts = line.split()

                if line_parts[0] == "d":
                    filetype = "directory"
                elif line_parts[0] == "l":
                    filetype = "link"
                else:
                    filetype = "file"

                manage = "dontmanage"
                path = line_parts[1]
                c.execute("INSERT INTO object SET path=%s, manage=%s, type=%s", (path, manage, filetype))

                out += template.format(path=path, comment=comment.strip(), lines=lines, line=line)

                comment = ""
                lines = ""

        except Exception as e:
            cherrypy.thread_data.db.rollback()
            raise
        else:
            cherrypy.thread_data.db.commit()
        return out + "</html></body>"
