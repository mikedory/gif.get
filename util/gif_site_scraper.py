# import stdlib stuff
debug = False

import sys
import os
import os.path
import urlparse
import re

# import our add-ons
import tornado
from tornado.options import define
import requests
from mongoengine import *
from bs4 import BeautifulSoup

# import other packages in other directories
# i am fairly sure this is a bad idea, but it works for now
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

# import our models
from app.models import Gif
from app.models import Gifsite

# import the util functions
from app.lib import util as util

# parse the command-line options
define("gif_site_url", help="the url of the site to scrape", type=str)
define("gif_site_name", help="the name of the site being scraped", type=str)
define("element", default="img", help="the type of tag to search for", type=str)
define("gif_tags", default=None, help="tags to apply to everything scraped", type=str)
define("gif_site_tags", default=None, help="tags to apply to everything scraped", type=str)
define("gif_site_description", default=None, help="tags to apply to everything scraped", type=str)
define("base_url", default="http://gif.dory.me/api/", help="name of the database", type=str)
define("mongo_url", default="localhost", help="location of mongodb", type=str)
define("mongo_port", default=27017, help="port mongodb is listening on", type=int)
define("mongo_dbname", default="gif-dot-get", help="name of the database", type=str)


# connect to mongodb using mongoengine
def get_db_connection():
    db = connect(
        tornado.options.options.mongo_dbname,
        host=tornado.options.options.mongo_url,
        port=tornado.options.options.mongo_port
    )
    return db


# the soup of gifs
def get_gifs_by_element(element, gif_site_url, gif_site_name, gif_tags, gif_site_tags, gif_site_description, api_base_url):

    # get all the gifs
    r = requests.get(gif_site_url)
    soup = BeautifulSoup(r.text)

    # split the tags, if there are any
    gif_tags = tags_split(gif_tags)
    gif_site_tags = tags_split(gif_site_tags)

    print "*** starting to scrape %s ***" % gif_site_url

    # grab all the links on the page
    for image in soup.findAll(element):

        # determine how to handle the target in question
        if "a" in element:
            target_url = image["href"]
        elif "img" in element:
            target_url = image["src"]
        else:
            sys.exit('Only "a" and "img" elements are supported.')

        # check the url, and update the target accordingly
        target_url_segments = util.url_split(target_url)
        if target_url_segments.netloc:
            # it is an absolute url
            target_image_base_url = target_url_segments.netloc
            target_image_url = target_url
        else:
            # it is a relative url
            target_image_base_url = gif_site_url
            if not re.match(r'http(s?)\:', gif_site_url):
                gif_site_url = 'http://' + gif_site_url
            target_image_url = gif_site_url + '/' + target_url

        # make sure we're only getting gifs, jpgs, and jpegs
        if any(extension in target_url for extension in ['gif', 'jpg', 'jpeg']):

            # make sure it's not a tracking pixel
            if not check_tracking_pixel(target_image_base_url):

                # define the document structure
                title = target_url_segments.path.split('/')[-1]
                slug = os.path.splitext(title)[0]
                img_url = target_image_url
                img_type = (os.path.splitext(title)[1]).split('.')[-1]
                host_name = gif_site_name
                host_url = gif_site_url
                gif_tags = gif_tags

                # define its location in the api
                href_base = util.url_join(api_base_url, 'gif/')
                href = util.url_join(href_base, slug)

                # debugginate
                if debug is True:
                    print '---'
                    print 'for tag %s of type "%s": ' % (target_url, element)
                    print 'title: %s' % title
                    print 'slug: %s' % slug
                    print 'img_url: %s' % img_url
                    print 'img_type: %s' % img_type
                    print 'host_name: %s' % host_name
                    print 'host_url: %s' % host_url
                    print 'gif_tags: %s' % gif_tags
                    print 'gif_site_tags: %s' % gif_site_tags
                    print 'href: %s' % href

                # in which gifs are found or created
                gif_upsert = update_gif_by_slug(title, slug, href, img_url, img_type, host_name, host_url, gif_tags)
                print gif_upsert

                # split out the http(s) if it exists
                if re.match(r'http(s?)\:', host_name):
                    gif_site_url_segments = util.url_split(host_name)
                    host_name = gif_site_url_segments.netloc

                # strip off .com and a few other fun things
                host_name_slug = host_name.strip('cmowz.')

                # define its location in the api
                host_href_base = util.url_join(api_base_url, 'gifsite/')
                host_href = util.url_join(host_href_base, host_name_slug)

                # check or create the gifsite
                gif_site_upsert = update_gif_site_by_slug(host_name, host_name_slug, host_href, host_url, gif_site_description, gif_site_tags)
                print gif_site_upsert

                # space things out
                print '---\n'

    print "done!"


# write in all the newfound gifs
def update_gif_by_slug(title, slug, href, img_url, img_type, host_name, host_url, gif_tags):

    # fetch the gif if it already exists, create it if it doesn't
    gif = Gif.objects(slug=slug).update_one(
        set__title=title,
        set__href=href,
        set__img_url=img_url,
        set__img_type=img_type,
        set__host_name=host_name,
        set__host_url=host_url,
        set__tags=gif_tags,
        upsert=True
    )

    # return the gif and the true/false of its creation
    return gif


# add the gifsite to the database
def update_gif_site_by_slug(title, slug, href, url, gif_site_description, gif_site_tags):

    # fetch the gifsite if it already exists, create it if it doesn't
    gif_site = Gifsite.objects(slug=slug).update_one(
        set__title=title,
        set__href=href,
        set__url=url,
        set__description=gif_site_description,
        set__tags=gif_site_tags,
        upsert=True
    )

    # return the gif and the true/false of its creation
    return gif_site


# split the tags (or return an empty list)
def tags_split(tags_string):
    if tags_string is not None:
        tags_list = tags_string.split(',')
    else:
        tags_list = []

    return tags_list


# get rid of tracking pixels
def check_tracking_pixel(url):

    known_tracking_pixel_urls = [
        'pixel.quantserve.com',
        'www.google-analytics.com'
    ]

    if url in known_tracking_pixel_urls:
        return True
    else:
        return False


# let's do this
if __name__ == "__main__":
    tornado.options.parse_command_line()
    get_db_connection()
    get_gifs_by_element(
        tornado.options.options.element,
        tornado.options.options.gif_site_url,
        tornado.options.options.gif_site_name,
        tornado.options.options.gif_tags,
        tornado.options.options.gif_site_tags,
        tornado.options.options.gif_site_description,
        tornado.options.options.base_url
    )
