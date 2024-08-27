import requests
from html.parser import HTMLParser
import pandas as pd
import os
from webinar.webinar_page_scraper import WebinarPageScraper, fetch_webinar_description_page

class WebinarParser(HTMLParser):
    """An HTMLParser class used to scrape Webinar data."""

    def __init__(self):
        super().__init__()
        self.webinars = []
        self.title_flag = False
        self.current_url = None

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for attr in attrs:
                if attr[0] == "href":
                    self.current_url = attr[1]

        if tag == "h3":
            for attr in attrs:
                if attr == ('class', 'h3 book-card__title'):
                    self.title_flag = True

    def handle_data(self, data):
        if self.title_flag and self.current_url:
            self.webinars.append({"Title": data.strip(), 
                                  "URL": self.current_url,
                                  "Subtitle": "",
                                  "Price": "",
                                  "Credit Hours": "",
                                  "Trainer": "",
                                  "Description": "",
                                  "Learning Objectives": "",
                                  "Target Audience": ""})
            self.title_flag = False
            self.current_url = None

    def handle_endtag(self, tag):
        if tag == "h3" and self.title_flag:
            self.title_flag = False

    def get_webinars(self):
        return self.webinars

def fetch_webinar_page(page_number):
    url = "https://achievecentre.com/wp-admin/admin-ajax.php?action=product_archive_filter"
    params = {
        'paged': page_number,
        'filter_term': 33
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

def fetch_all_webinars():
    print("*** FETCHING ALL WEBINARS ***")
    page_number = 1
    all_webinars = []
    while True:
        print(f"Fetching Webinar: page {page_number}...")
        posts_html = fetch_webinar_page(page_number)

        if not posts_html:
            break

        parser = WebinarParser()
        parser.feed(posts_html)
        webinars = parser.get_webinars()

        if not webinars:
            break

        for webinar in webinars:
            description_html = fetch_webinar_description_page(webinar['URL'])
            if description_html:
                page_parser = WebinarPageScraper()
                page_parser.feed(description_html)
                webinar_data = page_parser.get_webinar_information()
                webinar['Subtitle'] = webinar_data['webinar_subtitle']
                webinar['Price'] = webinar_data['webinar_price']
                webinar['Credit Hours'] = webinar_data['webinar_credit_hours']
                webinar['Trainer'] = webinar_data['webinar_trainer']
                webinar['Description'] = webinar_data['webinar_description']
                webinar['Learning Objectives'] = webinar_data['webinar_learning_objectives']
                webinar['Target Audience'] = webinar_data['webinar_target_audience']

        all_webinars.extend(webinars)
        page_number += 1
    return all_webinars

def get_desktop_path():
    """Get the path to the user's desktop directory."""
    return os.path.join(os.path.join(os.path.expanduser('~')), 'Documents')

def webinars_to_excel():
    all_webinars = fetch_all_webinars()
    print("**********************************")
    print(f"*** Found {len(all_webinars)} webinars!")
    print("**********************************")
    for webinar in all_webinars:
        print(f"{webinar['Title']} - {webinar['URL']}")

    print("*********************************")
    print("*** Exporting to excel file.")
    print("*********************************")

    # Get the path to user's desktop.
    desktop_path = get_desktop_path()
    output_file = os.path.join(desktop_path, 'achieve_webinar_web_data.xlsx')

    # Export webinar data to excel file.
    df = pd.DataFrame(all_webinars)
    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Webinars', index=False)
        workbook = writer.book
        worksheet = writer.sheets['Webinars']

        for idx, url in enumerate(df['URL'], start=2):
            worksheet.write_url(f'B{idx}', url)

    print("Webinar web data has been exported to achieve_webinar_web_data.xlsx in your documents folder.")

    # Open the created Excel file.
    if os.name == 'nt':  # Windows
        os.startfile(output_file)