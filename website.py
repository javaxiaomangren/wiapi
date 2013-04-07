#!/usr/bin/env python
import os, sys
import os.path
import time
import datetime
from tornado.options import options, define, parse_command_line
import tornado.auth
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

PROJECT_ROOT = os.path.realpath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(PROJECT_ROOT, os.pardir))

app_settings = {
    "api_prefix": "",
    "api_base": 'http://127.0.0.1',
    'cookie_secret': 'de2f899661fc8199f0d914abf1c21217',
    "xsrf_cookies": False,
    'native_locale': ['zh', 'zh_CN'],
    "debug": False,
    "autoescape": None,
}
try:
    from my_settings import load_tornado_settings
    load_tornado_settings(app_settings)
except:
    pass

import urls

from wiapi import api_manager, ex
apiurls = api_manager.get_urls()

#rest set
resturls = []
for uri in apiurls:
    ruri = uri[0]
    name =  uri[1].__module__
    if name.startswith("wiapi."):
        api_handler = name.split(".")[1]
        ruri = ruri.replace(":id","([\w\d]+)?")
        resturls.append((ruri,uri[1],))
apiurls = resturls

#setup docs
if app_settings.get('apidebug', False):
    from wiapi import doc

    apiurls = apiurls + [
            (r"/doc$", doc.ApiDocHandler),
            (r"/doc/apps$", doc.ApiAppKeyHandler),
            (r"/doc/example$", doc.ApiExampleHandler),
            (r"/map$", doc.ApiMapHandler),
    ]
    app_settings.update({
        "template_path": os.path.join(PROJECT_ROOT, "docs"),
        "static_path": os.path.join(PROJECT_ROOT, "docs"),
        "static_url_prefix": '%s/doc/static/' % app_settings.get('api_prefix', ''),
        })

handlers = [(app_settings.get('api_prefix', '') + u[0], u[1]) for u in apiurls]

from logger import api_log_function

class MyApplication(tornado.web.Application):
    def log_request(self, handler):
        if self.settings.get("record_ube",True):
            api_log_function(handler)

application = MyApplication(handlers, **app_settings)
define('port', type=int, default=80)

def main():
    http_server = tornado.httpserver.HTTPServer(application, no_keep_alive=True, xheaders=True)
    http_server.bind(options.port)
    if application.settings.get("debug"):
        http_server.start()
    else:
        http_server.start()
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    parse_command_line()
    main()
