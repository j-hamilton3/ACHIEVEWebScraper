import requests
from html.parser import HTMLParser
import pandas as pd
import cloudscraper

class TopicPageScraper(HTMLParser):
    """An HTMLParser class used to scrape Topic page data."""

    def __init__(self):
        super().__init__()
        self.subtitle = []
        self.training_options = []
        self.upcoming_trainings = []
        self.description = []

        self.subtitle_flag = False
        self.training_options_flag = False
        self.upcoming_trainings_flag = False
        self.description_flag = False

    def handle_starttag(self, tag, attrs):

        # Subtitle
        if tag == "h2":
            for attr in attrs:
                if attr[1] == "parent-topic__top__subtitle":
                    self.subtitle_flag = True

        # Training Options
        if tag == "div":
            for attr in attrs:
                if attr[1] == "parent-topic__main__formats__label":
                    self.training_options_flag = True

        # Upcoming Trainings
        if tag == "h5":
            for attr in attrs:
                if attr[1] == "event-card__date":
                    self.upcoming_trainings_flag = True

        # Description
        if tag == "div":
            for attr in attrs:
                if attr[1] == "parent-topic__top__desc":
                    self.description_flag = True
        
    def handle_data(self, data):
        if self.subtitle_flag:
            self.subtitle.append(data)

        if self.training_options_flag:
            self.training_options.append(data)

        if self.upcoming_trainings_flag:
            self.upcoming_trainings.append(data.replace(" \n", "").replace("\n", ""))

        if self.description_flag:
            self.description.append(data.replace("\n", ""))

    def handle_endtag(self, tag):

        # Subtitle
        if tag == "h2":
            self.subtitle_flag = False

        # Training Options
        if tag == "div":
            self.training_options_flag = False

        # Upcoming Trainings
        if tag == "h5":
            self.upcoming_trainings_flag = False
        
        # Description
        if tag == "div":
            self.description_flag = False

    def get_topic_information(self):
        return {
            "topic_subtitle": ' '.join(self.subtitle),
            "topic_training_options": ', '.join(self.training_options),
            "topic_upcoming_trainings": ' '.join(self.upcoming_trainings).strip(),
            "topic_description": ' '.join(self.description),
        }
    
def fetch_topic_description_page(url):
    cloud_scraper = cloudscraper.create_scraper()
    response = cloud_scraper.get(url)

    html_content = response.content.decode('utf-8')

    return html_content
