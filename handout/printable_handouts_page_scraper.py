import requests
from html.parser import HTMLParser
import pandas as pd
import cloudscraper

class PrintableHandoutsPageScraper(HTMLParser):
    """An HTMLParser class used to scrape Printable Handout page data."""

    def __init__(self):
        super().__init__()
        self.resource_link = []

        self.resource_link_flag = False
        self.inside_right_p_tag = False

    def handle_starttag(self, tag, attrs):
        if tag == "p":
            for attr in attrs:
                if attr[1] == "has-text-align-right":
                    self.inside_right_p_tag = True

        if tag == "a" and self.inside_right_p_tag:
            for attr in attrs:
                if attr[0] == "href" and attr[1].endswith(".pdf"):  # Added condition to check if URL ends with .pdf
                    self.resource_link.append(attr[1])

    def handle_endtag(self, tag):
        if tag == "p":
            self.inside_right_p_tag = False

    def get_printable_handout_information(self):
        return {"printable_handout_resource_link": ' '.join(self.resource_link)}
        
def fetch_printable_handout_description_page(url):
    cloud_scraper = cloudscraper.create_scraper()
    response = cloud_scraper.get(url)

    html_content = response.content.decode('utf-8')

    return html_content
