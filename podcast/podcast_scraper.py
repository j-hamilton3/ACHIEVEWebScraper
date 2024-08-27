import requests
from html.parser import HTMLParser
import pandas as pd
import os
from podcast.podcast_page_scraper import PodcastPageScraper, fetch_podcast_description_page

class PodcastParser(HTMLParser):
    """An HTMLParser class used to scrape Podcast data."""

    def __init__(self):
        super().__init__()
        self.podcasts = []
        self.title_flag = False
        self.current_url = None

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for attr in attrs:
                if attr[0] == "href":
                    self.current_url = attr[1]

        if tag == "h3":
            for attr in attrs:
                if attr == ('class', 'podcast-card__title'):
                    self.title_flag = True

    def handle_data(self, data):
        if self.title_flag and self.current_url:
            self.podcasts.append({"Title": data.strip(), "URL": self.current_url, "Description": "", "Audio Path": ""})
            self.title_flag = False
            self.current_url = None

    def handle_endtag(self, tag):
        if tag == "h3" and self.title_flag:
            self.title_flag = False

    def get_podcasts(self):
        return self.podcasts

def fetch_podcast_page(page_number):
    url = "https://achievecentre.com/wp-admin/admin-ajax.php?action=podcast_archive_filter"
    params = {
        'paged': page_number
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

def fetch_all_podcasts():
    print("*** FETCHING ALL PODCASTS ***")
    page_number = 1
    all_podcasts = []
    while True:
        print(f"Fetching Podcast: page {page_number}...")
        posts_html = fetch_podcast_page(page_number)

        if not posts_html:
            break

        parser = PodcastParser()
        parser.feed(posts_html)
        podcasts = parser.get_podcasts()

        if not podcasts:
            break
        for podcast in podcasts:
            description_html = fetch_podcast_description_page(podcast['URL'])
            if description_html:
                page_parser = PodcastPageScraper()
                page_parser.feed(description_html)
                podcast_data = page_parser.get_podcast_description_and_audio()
                podcast['Description'] = podcast_data['podcast_description']
                podcast['Audio Path'] = podcast_data['podcast_audio_path']
        
        all_podcasts.extend(podcasts)
        page_number += 1
    return all_podcasts

def get_desktop_path():
    """Get the path to the user's desktop directory."""
    return os.path.join(os.path.join(os.path.expanduser('~')), 'Documents')

def podcasts_to_excel():
    all_podcasts = fetch_all_podcasts()
    print("**********************************")
    print(f"*** Found {len(all_podcasts)} podcasts!")
    print("**********************************")
    for podcast in all_podcasts:
        print(f"{podcast['Title']} - {podcast['URL']}")

    print("*********************************")
    print("*** Exporting to excel file.")
    print("*********************************")

    # Get the path to user's desktop.
    desktop_path = get_desktop_path()
    output_file = os.path.join(desktop_path, 'achieve_podcast_web_data.xlsx')

    # Export podcast data to excel file.
    df = pd.DataFrame(all_podcasts)
    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Podcasts', index=False)
        workbook = writer.book
        worksheet = writer.sheets['Podcasts']

        for idx, url in enumerate(df['URL'], start=2):
            worksheet.write_url(f'B{idx}', url)

    print("Podcast web data has been exported to achieve_podcast_web_data.xlsx in your documents folder.")

    # Open the created Excel file.
    if os.name == 'nt':  # Windows
        os.startfile(output_file)