import urlparse


# prettily join urls
def url_join(url_base, url_to_join):

    # make sure the base has a trailing slash
    if not url_base.endswith('/'):
        url_base += '/'

    joined_url = urlparse.urljoin(url_base, url_to_join)

    return joined_url


# slice the url up into pieces
def url_split(url):
    segments = urlparse.urlsplit(url)
    return segments
