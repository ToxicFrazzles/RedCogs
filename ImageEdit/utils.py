import requests


def url_is_image(url):
	with requests.head(url) as r:
		return r.headers['content-type'].startswith("image/")