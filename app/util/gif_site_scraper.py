import os

import tornado
from tornado.options import define
import requests
from bs4 import BeautifulSoup

# parse the command-line options
define("gif_site_url", help="the url of the site to scrape", type=str)
define("gif_site_name", help="the name of the site being scraped", type=str)
define("element", default="a", help="the type of tag to search for", type=str)


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


if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = get_gifs_by_element(
        tornado.options.options.element,
        tornado.options.options.gif_site_url,
        tornado.options.options.gif_site_name)
