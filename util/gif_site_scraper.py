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
            target_image = image["href"]
        elif "img" in element:
            target_image = image["src"]
        else:
            print 'bananamonkeys'

        # make sure we're only getting gifs, jpgs, and jpegs
        if any(extension in target_image for extension in ['gif', 'jpg', 'jpeg']):

            # assemble the url and post body
            img_url = gif_site_url + target_image

            # define the document structure
            title = target_image
            slug = os.path.splitext(target_image)[0]
            img_url = gif_site_url + target_image
            img_type = os.path.splitext(target_image)[1].split('.')[1]
            host_name = gif_site_name
            host_url = gif_site_url
            tags = tags

            # debugginate
            print 'for tag %s of type "%s": ' % (image, element)
            print 'title: %s' % title
            print 'slug: %s' % slug
            print 'img_url: %s' % img_url
            print 'img_type: %s' % img_type
            print 'host_name: %s' % host_name
            print 'host_url: %s' % host_url
            print 'tags: %s' % tags
            print '---'

            # in which gifs are found or created
            upsert = update_gif_by_slug(title, slug, img_url, img_type, host_name, host_url, tags)

            print upsert


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


# check to see if there's a tld in this file name
def check_tld_list(file_to_check):
    tld_names = [
        ".aero",
        ".asia",
        ".biz",
        ".cat",
        ".com",
        ".coop",
        ".info",
        ".int",
        ".jobs",
        ".mobi",
        ".museum",
        ".name",
        ".net",
        ".org",
        ".post",
        ".pro",
        ".tel",
        ".travel",
        ".xxx",
        ".edu",
        ".gov",
        ".mil",
        ".ac",
        ".ad",
        ".ae",
        ".af",
        ".ag",
        ".ai",
        ".al",
        ".am",
        ".an",
        ".ao",
        ".aq",
        ".ar",
        ".as",
        ".at",
        ".au",
        ".aw",
        ".ax",
        ".az",
        ".ba",
        ".bb",
        ".bd",
        ".be",
        ".bf",
        ".bg",
        ".bh",
        ".bi",
        ".bj",
        ".bm",
        ".bn",
        ".bo",
        ".br",
        ".bs",
        ".bt",
        ".bv",
        ".bw",
        ".by",
        ".bz",
        ".ca",
        ".cc",
        ".cd",
        ".cf",
        ".cg",
        ".ch",
        ".ci",
        ".ck",
        ".cl",
        ".cm",
        ".cn",
        ".co",
        ".cr",
        ".cs",
        ".cu",
        ".cv",
        ".cx",
        ".cy",
        ".cz",
        ".dd",
        ".de",
        ".dj",
        ".dk",
        ".dm",
        ".do",
        ".dz",
        ".ec",
        ".ee",
        ".eg",
        ".eh",
        ".er",
        ".es",
        ".et",
        ".eu",
        ".fi",
        ".fj",
        ".fk",
        ".fm",
        ".fo",
        ".fr",
        ".ga",
        ".gb",
        ".gd",
        ".ge",
        ".gf",
        ".gg",
        ".gh",
        ".gi",
        ".gl",
        ".gm",
        ".gn",
        ".gp",
        ".gq",
        ".gr",
        ".gs",
        ".gt",
        ".gu",
        ".gw",
        ".gy",
        ".hk",
        ".hm",
        ".hn",
        ".hr",
        ".ht",
        ".hu",
        ".id",
        ".ie",
        ".il",
        ".im",
        ".in",
        ".io",
        ".iq",
        ".ir",
        ".is",
        ".it",
        ".je",
        ".jm",
        ".jo",
        ".jp",
        ".ke",
        ".kg",
        ".kh",
        ".ki",
        ".km",
        ".kn",
        ".kp",
        ".kr",
        ".kw",
        ".ky",
        ".kz",
        ".la",
        ".lb",
        ".lc",
        ".li",
        ".lk",
        ".lr",
        ".ls",
        ".lt",
        ".lu",
        ".lv",
        ".ly",
        ".ma",
        ".mc",
        ".md",
        ".me",
        ".mg",
        ".mh",
        ".mk",
        ".ml",
        ".mm",
        ".mn",
        ".mo",
        ".mp",
        ".mq",
        ".mr",
        ".ms",
        ".mt",
        ".mu",
        ".mv",
        ".mw",
        ".mx",
        ".my",
        ".mz",
        ".na",
        ".nc",
        ".ne",
        ".nf",
        ".ng",
        ".ni",
        ".nl",
        ".no",
        ".np",
        ".nr",
        ".nu",
        ".nz",
        ".om",
        ".pa",
        ".pe",
        ".pf",
        ".pg",
        ".ph",
        ".pk",
        ".pl",
        ".pm",
        ".pn",
        ".pr",
        ".ps",
        ".pt",
        ".pw",
        ".py",
        ".qa",
        ".re",
        ".ro",
        ".rs",
        ".ru",
        ".rw",
        ".sa",
        ".sb",
        ".sc",
        ".sd",
        ".se",
        ".sg",
        ".sh",
        ".si",
        ".sj",
        ".sk",
        ".sl",
        ".sm",
        ".sn",
        ".so",
        ".sr",
        ".ss",
        ".st",
        ".su",
        ".sv",
        ".sx",
        ".sy",
        ".sz",
        ".tc",
        ".td",
        ".tf",
        ".tg",
        ".th",
        ".tj",
        ".tk",
        ".tl",
        ".tm",
        ".tn",
        ".to",
        ".tp",
        ".tr",
        ".tt",
        ".tv",
        ".tw",
        ".tz",
        ".ua",
        ".ug",
        ".uk",
        ".us",
        ".uy",
        ".uz",
        ".va",
        ".vc",
        ".ve",
        ".vg",
        ".vi",
        ".vn",
        ".vu",
        ".wf",
        ".ws",
        ".ye",
        ".yt",
        ".yu",
        ".za",
        ".zm",
        ".zw"
    ]

    # split off the filename, if there is one
    name_to_check = os.path.splitext(file_to_check)[0]

    # if any(name in file_to_check for name in tld_names):
    if any(name in name_to_check for name in tld_names):
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
