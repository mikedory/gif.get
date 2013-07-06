# import stdlib stuff
import sys
import os
import os.path

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
def get_gifs_by_element(element, gif_site_url, gif_site_name):

    # get all the gifs
    r = requests.get(gif_site_url)
    soup = BeautifulSoup(r.text)

    # grab all the links on the page
    for image in soup.findAll(element):

        # make sure we're only getting gifs, jpgs, and jpegs
        if any(extension in image["href"] for extension in ['gif', 'jpg', 'jpeg']):

            # assemble the url and post body
            img_url = gif_site_url + image["href"]

            # define the document structure
            title = image["href"]
            slug = os.path.splitext(image["href"])[0]
            img_url = gif_site_url + image["href"]
            img_type = os.path.splitext(image["href"])[1].split('.')[1]
            host_name = gif_site_name
            host_url = gif_site_url

            # debugginate
            print 'for tag %s of type "%s": ' % (image, element)
            print title
            print slug
            print img_url
            print img_type
            print host_name
            print host_url
            print '---'

            # in which gifs are found or created
            upsert = update_gif_by_slug(title, slug, img_url, img_type, host_name, host_url)

            print upsert


# write in all the newfound gifs
def update_gif_by_slug(title, slug, img_url, img_type, host_name, host_url):

    # fetch the gif if it already exists, create it if it doesn't
    gif, created = Gif.objects.get_or_create(
        slug=slug,
        title=title,
        img_url=img_url,
        img_type=img_type,
        host_name=host_name,
        host_url=host_url
    )

    # return the gif and the true/false of its creation
    return gif, created


# let's do this
if __name__ == "__main__":
    tornado.options.parse_command_line()
    get_db_connection()
    get_gifs_by_element(
        tornado.options.options.element,
        tornado.options.options.gif_site_url,
        tornado.options.options.gif_site_name)
