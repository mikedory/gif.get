#!/usr/bin/env python

# import standard things
import os.path
import json
import random

# import tornado things
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import define

# import mongo things
from mongoengine import *

# import our models
from models import Gifsite
from models import Gif

# define the app settings
define("port", default=5000, help="run on the given port", type=int)
define("mongo_url", default="localhost", help="location of mongodb", type=str)
define("mongo_port", default=27017, help="port mongodb is listening on", type=int)
define("mongo_dbname", default="gif-dot-get", help="name of the database", type=str)


# application settings and handle mapping info
class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            # (r"/", IndexHandler),
            (r"/?([^/]+)?", GifHandler),
            (r"/gif/?([^/]+)?", GifHandler),
            (r"/gifsite/?([^/]+)?", GifsiteHandler)
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            debug=True,
        )

        # establish a db connection
        self.db = connect(
            tornado.options.options.mongo_dbname,
            host=tornado.options.options.mongo_url,
            port=tornado.options.options.mongo_port
        )

        # define the application
        tornado.web.Application.__init__(self, handlers, **settings)


# the main page
class IndexHandler(tornado.web.RequestHandler):
    def get(self, q=None):
        if 'GOOGLEANALYTICSID' in os.environ:
            google_analytics_id = os.environ['GOOGLEANALYTICSID']
        else:
            google_analytics_id = False

        self.render(
            "main.html",
            page_title='gif dot get',
            page_heading='gif.get',
            page_footer='by @mike_dory',
            google_analytics_id=google_analytics_id,
        )


# the main page
class GifHandler(tornado.web.RequestHandler):
    def get(self, slug):

        # if there's a gif requested, look it up
        if slug is not None:
            try:
                gif = Gif.objects.get(slug=slug)
            except DoesNotExist:
                gif = None

        # if none were requested, return one at random
        else:
            # I should probably do this method here instead:
            # http://stackoverflow.com/questions/2824157/random-record-from-mongodb
            # but for a tiny set it's fine for now
            gifs = Gif.objects.all()
            gif = random.choice(gifs)

        # if that produced a result, return it
        if gif is not None:
            response = {
                "title": gif["title"],
                "slug": gif["slug"],
                "img_url": gif["img_url"],
                "img_type": gif["img_type"],
                "host_name": gif["host_name"],
                "host_url": gif["host_url"],
                "tags": gif["tags"],
                "created_at": str(gif["created_at"])
            }

        # if that search came up empty, return a 404
        else:
            self.set_status(404)
            response = {
                "title": "404'd!",
                "status": "404",
            }

        # write it out
        self.set_header('Content-Type', 'application/javascript')
        self.write(json.dumps(response))


# the main page
class GifsiteHandler(tornado.web.RequestHandler):
    def get(self, slug):

        # if there's a gif requested, look it up
        if slug is not None:
            try:
                gifsite = Gifsite.objects.get(slug=slug)
            except DoesNotExist:
                gifsite = None

        # if none were requested, return one at random
        else:
            gifsites = Gifsite.objects.all()
            gifsite = random.choice(gifsites)

        # if that produced a result, return it
        if gifsite is not None:
            response = {
                "title": gifsite["title"],
                "slug": gifsite["slug"],
                "body": gifsite["body"],
                "tags": gifsite["tags"],
                "created_at": str(gifsite["created_at"])
            }

        # if that search came up empty, return a 404
        else:
            self.set_status(404)
            response = {
                "title": "404'd!",
                "status": "404",
            }

        # write it out
        self.set_header('Content-Type', 'application/javascript')
        self.write(json.dumps(response))


# RAMMING SPEEEEEEED!
def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(tornado.options.options.port)

    # start it up
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
