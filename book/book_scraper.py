import requests
from html.parser import HTMLParser
import pandas as pd
import os
from book.book_page_scraper import BookPageScraper, fetch_book_description_page

class BookParser(HTMLParser):
    """An HTMLParser class used to scrape Book data."""

    def __init__(self):
        super().__init__()
        self.books = []
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
            self.books.append({"Title": data.strip(), 
                               "URL": self.current_url,
                               "Subtitle": "",
                               "Price": "",
                               "Author": "",
                               "Short Description": "",
                               "Long Description": ""})
            self.title_flag = False
            self.current_url = None

    def handle_endtag(self, tag):
        if tag == "h3" and self.title_flag:
            self.title_flag = False

    def get_books(self):
        return self.books

def fetch_book_page(page_number):
    url = "https://achievecentre.com/product-category/book/"
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

def fetch_all_books():
    print("*** FETCHING ALL BOOKS ***")
    page_number = 1
    all_books = []
    while True:
        print(f"Fetching Book: page {page_number}...")
        posts_html = fetch_book_page(page_number)

        if not posts_html:
            break

        parser = BookParser()
        parser.feed(posts_html)
        books = parser.get_books()

        if not books:
            break

        for book in books:
            description_html = fetch_book_description_page(book['URL'])
            if description_html:
                page_parser = BookPageScraper()
                page_parser.feed(description_html)
                book_data = page_parser.get_book_information()

                book['Subtitle'] = book_data['book_subtitle']
                book['Price'] = book_data['book_price']
                book['Author'] = book_data['book_author']
                book['Short Description'] = book_data['book_short_description']
                book['Long Description'] = book_data['book_long_description']

        all_books.extend(books)
        page_number += 1
    return all_books

def get_documents_path():
    """Get the path to the user's documents directory."""
    return os.path.join(os.path.join(os.path.expanduser('~')), 'Documents')

def books_to_excel():
    all_books = fetch_all_books()

    print("**********************************")
    print(f"*** Found {len(all_books)} books!")
    print("**********************************")

    for book in all_books:
        print(f"{book['Title']} - {book['URL']}")

    print("*********************************")
    print("*** Exporting to excel file.")
    print("*********************************")

    # Get the path to user's desktop.
    documents_path = get_documents_path()
    output_file = os.path.join(documents_path, 'achieve_book_web_data.xlsx')

    # Export book data to excel file.
    df = pd.DataFrame(all_books)
    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Books', index=False)
        workbook = writer.book
        worksheet = writer.sheets['Books']

        for idx, url in enumerate(df['URL'], start=2):
            worksheet.write_url(f'B{idx}', url)

    print("Book web data has been exported to achieve_book_web_data.xlsx in your documents folder.")

    # Open the created Excel file.
    if os.name == 'nt':  # Windows
        os.startfile(output_file)
