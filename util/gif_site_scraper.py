# import stdlib stuff
import sys
import os
import os.path
import urlparse

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

# parse the command-line options
define("gif_site_url", help="the url of the site to scrape", type=str)
define("gif_site_name", help="the name of the site being scraped", type=str)
define("element", default="a", help="the type of tag to search for", type=str)
define("tags", default=None, help="tags to apply to everything scraped", type=str)
define("mongo_url", default="localhost", help="location of mongodb", type=str)
define("mongo_port", default=27017, help="port mongodb is listening on", type=int)
define("mongo_dbname", default="gif-dot-get", help="name of the database", type=str)


def get_db_connection():
    db = connect(
        tornado.options.options.mongo_dbname,
        host=tornado.options.options.mongo_url,
        port=tornado.options.options.mongo_port
    )

    return db


# the soup of gifs
def get_gifs_by_element(element, gif_site_url, gif_site_name, tags):

    # get all the gifs
    r = requests.get(gif_site_url)
    soup = BeautifulSoup(r.text)

    tags = tags.split(',')

    # grab all the links on the page
    for image in soup.findAll(element):

        if "a" in element:
            target_url = image["href"]
        elif "img" in element:
            target_url = image["src"]
        else:
            sys.exit('Only "a" and "img" elements are supported.')

        target_url_segments = url_split(target_url)
        if target_url_segments.netloc:
            # it is an absolute url
            target_image_url = target_url_segments.netloc
        else:
            # it is a relative url
            target_image_url = gif_site_url

        # make sure we're only getting gifs, jpgs, and jpegs
        if any(extension in target_url for extension in ['gif', 'jpg', 'jpeg']):

            if not check_tracking_pixel(target_url):

                # define the document structure
                title = target_url_segments.path.split('/')[-1]
                slug = os.path.splitext(title)[0]
                img_url = target_image_url
                img_type = (os.path.splitext(title)[1]).split('.')[-1]
                host_name = gif_site_name
                host_url = gif_site_url
                tags = tags

                # debugginate
                print '---'
                print 'for tag %s of type "%s": ' % (target_url, element)
                print 'title: %s' % title
                print 'slug: %s' % slug
                print 'img_url: %s' % img_url
                print 'img_type: %s' % img_type
                print 'host_name: %s' % host_name
                print 'host_url: %s' % host_url
                print 'tags: %s' % tags

                # in which gifs are found or created
                upsert = update_gif_by_slug(title, slug, img_url, img_type, host_name, host_url, tags)

                print upsert
                print '---\n'


# write in all the newfound gifs
def update_gif_by_slug(title, slug, img_url, img_type, host_name, host_url, tags):

    # fetch the gif if it already exists, create it if it doesn't
    gif, created = Gif.objects.get_or_create(
        slug=slug,
        title=title,
        img_url=img_url,
        img_type=img_type,
        host_name=host_name,
        host_url=host_url,
        tags=tags
    )

    # return the gif and the true/false of its creation
    return gif, created


# slice the url up into pieces
def url_split(url):
    segments = urlparse.urlsplit(url)
    return segments


# get rid of tracking pixels
def check_tracking_pixel(url):

    known_tracking_pixel_urls = [
        'pixel.quantserve.com',
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
        tornado.options.options.tags
    )
