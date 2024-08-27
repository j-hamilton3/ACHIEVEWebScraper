import requests
from html.parser import HTMLParser
import pandas as pd
import os
from topic.topic_page_scraper import TopicPageScraper, fetch_topic_description_page

class TopicParser(HTMLParser):
    """An HTMLParser class used to scrape Topic data."""

    def __init__(self):
        super().__init__()
        self.topics = []
        self.title_flag = False
        self.current_url = None

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for attr in attrs:
                if attr[0] == "href":
                    self.current_url = attr[1]

        if tag == "h3":
            for attr in attrs:
                if attr == ('class', 'h3 topic-card__title'):
                    self.title_flag = True

    def handle_data(self, data):
        if self.title_flag and self.current_url:
            title = data.strip()
            if title.endswith('-'):
                title = title.rstrip('-')
            self.topics.append({"Title": title, 
                                "URL": self.current_url,
                                "Subtitle": "",
                                "Training Options": "",
                                "Upcoming Trainings": "",
                                "Description": ""})
            self.title_flag = False
            self.current_url = None

    def handle_endtag(self, tag):
        if tag == "h3" and self.title_flag:
            self.title_flag = False

    def get_topics(self):
        return self.topics

def fetch_topic_page(page_number):
    url = "https://achievecentre.com/wp-admin/admin-ajax.php?action=topic_archive_filter"
    params = {
        'paged': page_number,
    }
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }
    response = requests.get(url, params=params, headers=headers)

    if response.status_code != 200:
        return None

    # Check if the response content type is JSON or not
    if 'application/json' in response.headers.get('Content-Type', ''):
        json_response = response.json()
        return json_response.get('data', {}).get('posts', '') 
    else:
        return response.text

def fetch_all_topics():
    print("*** FETCHING ALL TOPICS ***")
    page_number = 1
    all_topics = []
    while True:
        print(f"Fetching Topic: page {page_number}...")
        posts_html = fetch_topic_page(page_number)

        if not posts_html:
            break

        parser = TopicParser()
        parser.feed(posts_html)
        topics = parser.get_topics()

        if not topics:
            break

        for topic in topics:
            description_html = fetch_topic_description_page(topic['URL'])
            if description_html:
                page_parser = TopicPageScraper()
                page_parser.feed(description_html)
                topic_data = page_parser.get_topic_information()

                topic['Subtitle'] = topic_data['topic_subtitle']
                topic['Training Options'] = topic_data['topic_training_options']
                topic['Upcoming Trainings'] = topic_data['topic_upcoming_trainings']
                topic['Description'] = topic_data['topic_description']

        all_topics.extend(topics)
        page_number += 1
    return all_topics

###########################

def get_desktop_path():
    """Get the path to the user's desktop directory."""
    return os.path.join(os.path.join(os.path.expanduser('~')), 'Documents')

def topics_to_excel():
    all_topics = fetch_all_topics()
    print("**********************************")
    print(f"*** Found {len(all_topics)} topics!")
    print("**********************************")
    for topic in all_topics:
        print(f"{topic['Title']} - {topic['URL']}")

    print("*********************************")
    print("*** Exporting to excel file.")
    print("*********************************")

    # Get the path to user's desktop.
    desktop_path = get_desktop_path()
    output_file = os.path.join(desktop_path, 'achieve_topic_web_data.xlsx')

    # Export topic data to excel file.
    df = pd.DataFrame(all_topics)
    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Topics', index=False)
        workbook = writer.book
        worksheet = writer.sheets['Topics']

        for idx, url in enumerate(df['URL'], start=2):
            worksheet.write_url(f'B{idx}', url)

    print("Topic web data has been exported to achieve_topic_web_data.xlsx in your documents folder.")

    # Open the created Excel file.
    if os.name == 'nt':  # Windows
        os.startfile(output_file)

