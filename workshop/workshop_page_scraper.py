import requests
from html.parser import HTMLParser
import pandas as pd
import cloudscraper

class WorkshopPageScraper(HTMLParser):
    """An HTMLParser class used to scrape Workshop page data."""

    def __init__(self):
        super().__init__()
        self.subtitle = []
        self.price = []
        self.credit_hours = []
        self.trainer = []
        self.description = []
        self.learning_objectives = []
        self.topics_reviewed = []
        self.target_audience = []

        self.subtitle_flag = False
        self.price_flag = False
        self.credit_hours_flag = False
        self.trainer_flag = False
        self.description_flag = False
        self.learning_objectives_flag = False
        self.topics_reviewed_flag = False
        self.target_audience_flag = False

    def handle_starttag(self, tag, attrs):
        # Subtitles
        if tag == "h3":
            for attr in attrs:
                if attr[1] == "top-title__subtitle":
                    self.subtitle_flag = True

        # Price
        if tag == "div":
            for attr in attrs:
                if attr[1] == " product-price":
                    self.price_flag = True

        # Credit Hours
        if tag == "div":
            for attr in attrs:
                if attr[1] == "on-demand-workshop__credit-hours--hours":
                    self.credit_hours_flag = True
        
        # Trainer
        if tag == "p":
            for attr in attrs:
                if attr[1] == "on-demand-workshop__trainer":
                    self.trainer_flag = True

        # Learning Objectives
        if tag == "div":
            for attr in attrs:
                if attr[1] == "parent-topic__learning-objectives":
                    self.learning_objectives_flag = True

        # Topics Reviewed
        if tag == "div":
            for attr in attrs:
                if attr[1] == "parent-topic__topics-reviewed":
                    self.topics_reviewed_flag = True

        # Target Audience
        if tag == "div":
            for attr in attrs:
                if attr[1] == "parent-topic__target-audicence":
                    self.target_audience_flag = True

        # Description
        if tag == "div":
            for attr in attrs:
                if attr[1] == "spu-placeholder":
                    self.description_flag = True
        

    def handle_data(self, data):
        # Subtitles
        if self.subtitle_flag:
            self.subtitle.append(data)

        # Price
        if self.price_flag:
            self.price.append(data.strip())

        # Credit Hours
        if self.credit_hours_flag:
            self.credit_hours.append(data)

        # Trainer
        if self.trainer_flag:
            self.trainer.append(data.replace("\n", " ").replace("Trainer:", "").strip())

        # Learning Objectives
        if self.learning_objectives_flag:
            self.learning_objectives.append(data.replace("Learning Objectives", "").strip())

        # Topics Reviewed
        if self.topics_reviewed_flag:
            self.topics_reviewed.append(data.strip())

        # Target Audience
        if self.target_audience_flag:
            self.target_audience.append(data.replace("Target Audience", "").strip())

        # Description
        if self.description_flag:
            self.description.append(data.strip())

    def handle_endtag(self, tag):
        # Subtitles
        if tag == "h3":
            self.subtitle_flag = False

        # Price
        if tag == "div":
            self.price_flag = False
            self.credit_hours_flag = False
            self.learning_objectives_flag = False
            self.topics_reviewed_flag = False
            self.target_audience_flag = False

        # Trainer
        if tag == "p":
            self.trainer_flag = False
            self.description_flag = False

    def get_workshop_information(self):
        return {
            "workshop_subtitle": ' '.join(self.subtitle),
            "workshop_price": ' '.join(self.price),
            "workshop_credit_hours": ' '.join(self.credit_hours),
            "workshop_trainer": ' '.join(self.trainer).strip(),
            "workshop_description": ' '.join(self.description),
            "workshop_learning_objectives": ' '.join(self.learning_objectives).strip(),
            "workshop_topics_reviewed": ' '.join(self.topics_reviewed).strip(),
            "workshop_target_audience": ' '.join(self.target_audience).strip(),
        }

def fetch_workshop_description_page(url):
    cloud_scraper = cloudscraper.create_scraper()
    response = cloud_scraper.get(url)

    html_content = response.content.decode('utf-8')

    return html_content
