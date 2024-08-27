from blog.blog_scraper import fetch_all_blogs
from book.book_scraper import fetch_all_books
from handout.printable_handouts_scraper import fetch_all_handouts
from podcast.podcast_scraper import fetch_all_podcasts
from topic.topic_scraper import fetch_all_topics
from webinar.webinar_scraper import fetch_all_webinars
from workshop.workshop_scraper import fetch_all_workshops
import time
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import os

def fetch_all_resources():
    """Fetch all resources concurrently using threading."""
    with ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(fetch_all_blogs): 'blogs',
            executor.submit(fetch_all_books): 'books',
            executor.submit(fetch_all_handouts): 'handouts',
            executor.submit(fetch_all_podcasts): 'podcasts',
            executor.submit(fetch_all_topics): 'topics',
            executor.submit(fetch_all_webinars): 'webinars',
            executor.submit(fetch_all_workshops): 'workshops',
        }

        results = {}
        for future in futures:
            resource_type = futures[future]
            try:
                results[resource_type] = future.result()
            except Exception as e:
                print(f"Error fetching {resource_type}: {e}")

    return results

def get_documents_path():
    """Gets the path to the user's documents folder."""
    return os.path.join(os.path.expanduser('~'), 'Documents')

def all_resources_to_excel():
    """Gets all resources from webscrapers, then exports to Excel."""

    start_time = time.time()

    print("*** FETCHING ALL RESOURCES ***")
    resources = fetch_all_resources()

    end_time = time.time()
    elapsed_time = end_time - start_time
    
    print(f"*** COMPLETED IN {elapsed_time:.2f} SECONDS. ***")

    # Define the path to the Excel file
    documents_path = get_documents_path()
    output_file = os.path.join(documents_path, "achieve_all_web_data.xlsx")

    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        for resource_type, data in resources.items():
            df = pd.DataFrame(data)
            df.to_excel(writer, sheet_name=resource_type.capitalize(), index=False)

    print(f"Web data has been exported to achieve_all_web_data.xlsx in your documents folder.")
    
    # Open the created Excel file.
    if os.name == 'nt':  # Windows
        os.startfile(output_file)

