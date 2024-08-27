import requests
from html.parser import HTMLParser
import pandas as pd
import os
from handout.printable_handouts_page_scraper import PrintableHandoutsPageScraper, fetch_printable_handout_description_page

class HandoutsParser(HTMLParser):
    """An HTMLParser class used to scrape Printable Handouts data."""

    def __init__(self):
        super().__init__()
        self.handouts = []
        self.title_flag = False
        self.current_url = None

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for attr in attrs:
                if attr[0] == "href":
                    self.current_url = attr[1]

        if tag == "h4":
            for attr in attrs:
                if attr == ('class', 'h4 resources-grid__content--title'):
                    self.title_flag = True

    def handle_data(self, data):
        if self.title_flag and self.current_url:
            self.handouts.append({"Title": data.strip(), 
                                  "URL": self.current_url,
                                  "Resource Link": "",})
            self.title_flag = False
            self.current_url = None

    def handle_endtag(self, tag):
        if tag == "h4" and self.title_flag:
            self.title_flag = False

    def get_handouts(self):
        return self.handouts

def fetch_handouts_page():
    url = "https://achievecentre.com/resources/printable-handouts/"
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return None

    return response.text

def fetch_all_handouts():
    print("*** FETCHING ALL HANDOUTS ***")
    posts_html = fetch_handouts_page()

    if not posts_html:
        return []

    parser = HandoutsParser()
    parser.feed(posts_html)
    print("Fetching Handout: page 1...")
    handouts = parser.get_handouts()

    for handout in handouts:
        description_html = fetch_printable_handout_description_page(handout['URL'])

        if description_html:
            page_parser = PrintableHandoutsPageScraper()
            page_parser.feed(description_html)
            handout_data = page_parser.get_printable_handout_information()

            handout['Resource Link'] = handout_data['printable_handout_resource_link']

    return handouts

def get_documents_path():
    """Gets the path to the user's documents folder."""
    return os.path.join(os.path.join(os.path.expanduser('~')), 'Documents')

def handouts_to_excel():
    all_handouts = fetch_all_handouts()
    print("**********************************")
    print(f"*** Found {len(all_handouts)} handouts!")
    print("**********************************")
    for handout in all_handouts:
        print(f"{handout['Title']} - {handout['URL']}")

    print("*********************************")
    print("*** Exporting to excel file.")
    print("*********************************")

    # Get the path to user's desktop.
    documents_path = get_documents_path()
    output_file = os.path.join(documents_path, 'achieve_handout_web_data.xlsx')

    # Export handout data to excel file.
    df = pd.DataFrame(all_handouts)
    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Handouts', index=False)
        workbook = writer.book
        worksheet = writer.sheets['Handouts']

        for idx, url in enumerate(df['URL'], start=2):
            worksheet.write_url(f'B{idx}', url)

    print("Handout web data has been exported to achieve_handout_web_data.xlsx in your documents folder.")

    # Open the created Excel file.
    if os.name == 'nt':  # Windows
        os.startfile(output_file)