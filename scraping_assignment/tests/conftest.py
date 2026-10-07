import pytest
import requests


class FakeResponse:
    def __init__(self, text, status=200):
        self.text = text
        self.status = status
        self.encoding = None

    def raise_for_status(self):
        if self.status >= 400:
            raise requests.HTTPError(f"status {self.status}")


class FakeSession:
    def __init__(self, pages):
        self.pages = pages

    def get(self, url, timeout=None):
        if url not in self.pages:
            raise requests.ConnectionError(f"cannot reach {url}")
        return FakeResponse(self.pages[url])


@pytest.fixture
def make_session():
    return FakeSession


def book_html(title, price="\u00a310.00", rating="Three", href="book/index.html"):
    return (
        f'<article class="product_pod"><p class="star-rating {rating}"></p>'
        f'<h3><a href="{href}" title="{title}">{title[:5]}...</a></h3>'
        f'<div class="product_price"><p class="price_color">{price}</p></div></article>'
    )


def quote_html(text, author, tags):
    tag_links = "".join(f'<a class="tag" href="/tag/{t}/">{t}</a>' for t in tags)
    return (
        f'<div class="quote"><span class="text">\u201c{text}\u201d</span>'
        f'<span>by <small class="author">{author}</small></span>'
        f'<div class="tags">{tag_links}</div></div>'
    )


def page_html(items, next_href=None):
    nxt = f'<ul class="pager"><li class="next"><a href="{next_href}">next</a></li></ul>' if next_href else ""
    return f"<html><body>{''.join(items)}{nxt}</body></html>"
