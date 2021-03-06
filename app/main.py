#!/usr/bin/env python

# import standard things
import os.path
import json
import random
import logging

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

# import our lib files
import lib.api as api
import lib.util as util

# define the app settings
define("port", default=5000, help="run on the given port", type=int)
define("base_url", default="http://gif.dory.me/api/", help="name of the database", type=str)
define("mongo_url", default="localhost", help="location of mongodb", type=str)
define("mongo_port", default=27017, help="port mongodb is listening on", type=int)
define("mongo_dbname", default="gif-dot-get", help="name of the database", type=str)


# application settings and handle mapping info
class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", IndexHandler),
            (r"/api/?", RootHandler),
            (r"/api/gif/random/([^/]+)?/?", RandomGifHandler),
            (r"/api/gif/([^/]+)?", GifHandler),
            (r"/api/gif/([^/]+)/([^/]+)?/?", GifHandler),
            (r"/api/gifsite/([^/]+)?", GifsiteHandler)
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


# the base api endpoint
class RootHandler(tornado.web.RequestHandler):
    def get(self, q=None):

        # define the API base url
        api_base = tornado.options.options.base_url

        # describe the current available API endpoints
        # note: these must *not* have a leading slash
        response = {
            "gif": util.url_join(api_base, "gif/"),
            "gifsite": util.url_join(api_base, "gifsite/"),
            "random": util.url_join(api_base, "gif/random"),
        }

        # write it out
        self.set_header('Content-Type', 'application/javascript')
        self.write(json.dumps(response))


# the base gif endpoint
class GifHandler(tornado.web.RequestHandler):
    def get(self, slug, q=None):

        print slug
        print q

        query_type = self.get_argument('type', 'gif')
        query_limit = self.get_argument('limit', '25')
        query_redirect = self.get_argument('redirect', 'False')
        query_order_by = self.get_argument('sort', '-created_at')

        # if there's a gif requested, look it up
        if slug is not None:
            try:
                gif = Gif.objects.get(img_type=query_type, slug=slug)
                response = api.format_gif_for_json_response(gif)

                # if a redirect was requested, nicely do so
                if any(value in query_redirect for value in ['True', 'true']) or q == 'image':
                    self.redirect(response["img_url"])

            except DoesNotExist:
                # if that query came up empty, return a 404
                self.set_status(404)
                response = api.format_404_for_json_response()

        # if no gif was requested, fetch them all
        else:
            # get every entry matching the optional type and limit filters
            gifs = Gif.objects(img_type=query_type).order_by(query_order_by)[:int(query_limit)]

            # if that query produced a result, return it
            response_list = []
            for gif in gifs:
                single_response = api.format_gif_for_json_response(gif)
                response_list.append(single_response)
            response = {
                "gifs": response_list
            }

        # write it out
        self.set_header('Content-Type', 'application/javascript')
        self.write(json.dumps(response))


# the main endpoint
class RandomGifHandler(tornado.web.RequestHandler):
    def get(self, q=None):

        print q
        print 'wat'

        # parse the filters off the command line
        query_type = self.get_argument('type', 'gif')
        query_redirect = self.get_argument('redirect', 'False')

        # return a gif at random
        gifs = Gif.objects(img_type=query_type)
        gif = random.choice(gifs)

        # if that query produced a result, return it
        if gif is not None:
            response = api.format_gif_for_json_response(gif)

        # if that query came up empty, return a 404
        else:
            self.set_status(404)
            response = api.format_404_for_json_response()

        # if a redirect was requested, nicely do so
        if any(value in query_redirect for value in ['True', 'true']) or q == 'image':
            self.redirect(response["img_url"])
        else:
            # write it out
            self.set_header('Content-Type', 'application/javascript')
            self.write(json.dumps(response))


# the base gifsite endpoint
class GifsiteHandler(tornado.web.RequestHandler):
    def get(self, slug):

        query_limit = self.get_argument('limit', '25')
        query_order_by = self.get_argument('sort', '-created_at')

        # if there's a gif requested, look it up
        if slug is not None:
            try:
                gifsite = Gifsite.objects.get(slug=slug)
                response = api.format_gifsite_for_json_response(gifsite)

            except DoesNotExist:
                # if that query came up empty, return a 404
                self.set_status(404)
                response = api.format_404_for_json_response()

        # if no gifsite was requested, fetch them all
        else:
            # get every entry matching the optional type and limit filters
            gifsites = Gifsite.objects.order_by(query_order_by)[:int(query_limit)]

            # if that query produced a result, return it
            response_list = []
            for gifsite in gifsites:
                single_response = api.format_gifsite_for_json_response(gifsite)
                response_list.append(single_response)
            response = {
                "gifsites": response_list
            }

        # write it out
        self.set_header('Content-Type', 'application/javascript')
        self.write(json.dumps(response))


# RAMMING SPEEEEEEED!
def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    logging.info('Firing up Tornado on port %d...' % tornado.options.options.port)
    http_server.listen(tornado.options.options.port)

    # start it up
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
