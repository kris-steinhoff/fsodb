import os
import ConfigParser

import cherrypy
import MySQLdb

import fsodb

class Root(object):

    @cherrypy.expose
    def index(self):
        return """<a href="import">import</a>"""

if __name__ == '__main__':

    if os.path.isfile("config/server.cp.cfg"):
        cherrypy.config.update("config/server.cp.cfg")

    def db_connect(thread_index):
        # Thread-safe implementation: http://tools.cherrypy.org/wiki/Databases
        config = ConfigParser.SafeConfigParser()
        config.read("config/db.cfg")

        # Create a connection and store it in the current thread
        cherrypy.thread_data.db = MySQLdb.connect(**dict(config.items("mysql")))
        #print "connect to database: {db_obj}".format(db_obj=cherrypy.thread_data.db)

    # Tell CherryPy to call "connect" for each thread, when it starts up
    cherrypy.engine.subscribe('start_thread', db_connect)

    app = cherrypy.tree.mount(Root(), "/")
    cherrypy.tree.mount(fsodb.util.Import(), "/import", {"/": {"request.dispatch": cherrypy.dispatch.MethodDispatcher()}})

    if hasattr(cherrypy.engine, 'block'):
        # 3.1 syntax
        cherrypy.engine.start()
        cherrypy.engine.block()
    else:
        # 3.0 syntax
        cherrypy.server.quickstart()
        cherrypy.engine.start()
