from html.parser import HTMLParser
import pandas as pd
import cloudscraper

class BookPageScraper(HTMLParser):
    """An HTMLParser class used to scrape Book page data."""

    def __init__(self):
        super().__init__()
        self.subtitle = []
        self.price = []
        self.author = []
        self.short_description = []
        self.long_description = []

        self.subtitle_flag = False
        self.price_flag = False
        self.author_flag = False
        self.short_description_flag = False
        self.long_description_flag = False

    def handle_starttag(self, tag, attrs):
        # Subtitle
        if tag == "h3":
            for attr in attrs:
                if attr[1] == "book-product__banner__subtitle":
                    self.subtitle_flag = True
        # Price
        if tag == "span":
            for attr in attrs:
                if attr[1] == "product-price__regular ":
                    self.price_flag = True

        # Author
        if tag == "p":
            for attr in attrs:
                if attr[1] == "book_author":
                    self.author_flag = True

        # Short Description
        if tag == "p":
            for attr in attrs:
                if attr[1] == "book-product__desc--text":
                    self.short_description_flag = True

        # Long Description
        if tag == "div":
            for attr in attrs:
                if attr[1] == "book-info__left col-xs-12 col-md-6 col-lg-7":
                    self.long_description_flag = True


    def handle_data(self, data):
        if self.subtitle_flag:
            self.subtitle.append(data.strip())

        if self.price_flag:
            self.price.append(data)

        if self.author_flag:
            self.author.append(data.replace("\n", "").replace("Author:", "").replace("Authors:", "").strip())

        if self.short_description_flag:
            self.short_description.append(data.replace("\n", ""))

        if self.long_description_flag:
            self.long_description.append(data.replace("\n", "").replace("Description", "").replace("\xa0", " "))

    def handle_endtag(self, tag):
        # Subtitle
        if tag == "h3":
            self.subtitle_flag = False
        
        # Price
        if tag == "span":
            self.price_flag = False

        # Author
        if tag == "p":
            self.author_flag = False

        # Short Description
        if tag == "div":
            self.short_description_flag = False

        # Long Description
        if tag == "div":
            self.long_description_flag = False

    def get_book_information(self):
        return {
            "book_subtitle": ''.join(self.subtitle),
            "book_price": ''.join(self.price),
            "book_author": ''.join(self.author),
            "book_short_description": ''.join(self.short_description),
            "book_long_description": ''.join(self.long_description),
        }
    
def fetch_book_description_page(url):
    cloud_scraper = cloudscraper.create_scraper()
    response = cloud_scraper.get(url)

    html_content = response.content.decode('utf-8')

    return html_content
