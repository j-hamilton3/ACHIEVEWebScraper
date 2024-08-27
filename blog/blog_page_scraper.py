import requests 
from html.parser import HTMLParser
import pandas as pd
import cloudscraper

class BlogPageScraper(HTMLParser):
    """An HTMLParser class used to scraper Blog page data."""

    def __init__(self):
        super().__init__()
        self.image = []
        self.content = []
        self.trainer = []

        self.content_flag = False
        self.trainer_flag = False

    def handle_starttag(self, tag, attrs):

        # Image
        if tag == "div":
            for attr in attrs:
                if attr[1] == "article-banner__image":
                    for attr_key, attr_value in attrs:
                        if attr_key == "style":
                            url_start = attr_value.find('url(') + 4
                            url_end = attr_value.find(')', url_start)
                            self.image = attr_value[url_start:url_end]

        # Content
        if tag == "div":
            for attr in attrs:
                if attr[1] == "article-body":
                    self.content_flag = True

        if tag == "hr":
            self.content_flag = False

        # Trainer
        if tag == "h4":
            for attr in attrs:
                if attr[1] == "h4 blog-author__info-name":
                    self.trainer_flag = True

    def handle_data(self, data):
        if self.content_flag:
            self.content.append(data)

        if self.trainer_flag:
            self.trainer.append(data)

    def handle_endtag(self, tag):
        if tag == "h4":
            self.trainer_flag = False

    def get_blog_information(self):
        return {
            "blog_image": self.image,
            "blog_content": ' '.join(self.content).replace(" \n", "").replace("\n", "").replace(" \xa0", "").replace("\xa0", "").strip(),
            "blog_trainer":' '.join(self.trainer),
        }

def fetch_blog_description_page(url):
    cloud_scraper = cloudscraper.create_scraper()
    response = cloud_scraper.get(url)

    html_content = response.content.decode('utf-8')

    return html_content
