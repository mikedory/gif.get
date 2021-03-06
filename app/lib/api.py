

# format gifs for json output
def format_gif_for_json_response(gif):
    single_response = {
        "title": gif["title"],
        "slug": gif["slug"],
        "img_url": gif["img_url"],
        "img_type": gif["img_type"],
        "host_name": gif["host_name"],
        "host_url": gif["host_url"],
        "tags": gif["tags"],
        "href": gif["href"],
        "created_at": str(gif["created_at"])
    }
    return single_response


# format gifsites for json output
def format_gifsite_for_json_response(gifsite):
    single_response = {
        "title": gifsite["title"],
        "slug": gifsite["slug"],
        "url": gifsite["url"],
        "description": gifsite["description"],
        "tags": gifsite["tags"],
        "href": gifsite["href"],
        "created_at": str(gifsite["created_at"])
    }
    return single_response


# format 404s for json output
def format_404_for_json_response():
    single_response = {
        "title": "404'd!",
        "status": "404",
    }
    return single_response
