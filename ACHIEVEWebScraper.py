from tkinter import *
from tkinter import messagebox
import threading
from blog.blog_scraper import blogs_to_excel
from book.book_scraper import books_to_excel
from handout.printable_handouts_scraper import handouts_to_excel
from podcast.podcast_scraper import podcasts_to_excel
from topic.topic_scraper import topics_to_excel
from webinar.webinar_scraper import webinars_to_excel
from workshop.workshop_scraper import workshops_to_excel
from combined_scraper import all_resources_to_excel

class Application:
    def __init__(self, root):
        self.root = root
        self.root.title("ACHIEVE Web Scraper")
        self.root.geometry('400x350')
        self.root.resizable(False, False)

        self.root_destroyed = False

        # Frame for "Scrape all data" section.
        self.all_data_frame = Frame(self.root)
        self.all_data_frame.pack(pady=20)

        self.all_data_label = Label(self.all_data_frame, text='Scrape all data from achievecentre.com:')
        self.all_data_label.pack()

        self.all_data_time_warning = Label(self.all_data_frame, text='(This takes around 8 minutes.)')
        self.all_data_time_warning.pack()

        vertical_space = Label(self.all_data_frame, text="")
        vertical_space.pack()

        self.all_data_button = Button(self.all_data_frame, text="Get All Data", width=20, command=self.specific_to_excel(all_resources_to_excel))
        self.all_data_button.pack()

        # Frame for "Scrape specific data" section.
        self.specific_data_frame = Frame(self.root)
        self.specific_data_frame.pack(pady=10)

        self.specific_data_label = Label(self.specific_data_frame, text='Scrape specific data from achievecentre.com:')
        self.specific_data_label.pack()

        self.specific_buttons_frame = Frame(self.specific_data_frame)
        self.specific_buttons_frame.pack(pady=10)

        self.buttons = [
            ("Get Blog Data", blogs_to_excel),
            ("Get Book Data", books_to_excel),
            ("Get Handout Data", handouts_to_excel),
            ("Get Podcast Data", podcasts_to_excel),
            ("Get Topic Data", topics_to_excel),
            ("Get Webinar Data", webinars_to_excel),
            ("Get Workshop Data", workshops_to_excel)
        ]

        self.buttons_widgets = [self.all_data_button]

        for i, (text, command) in enumerate(self.buttons):
            row = i // 2
            col = i % 2
            button = Button(self.specific_buttons_frame, text=text, command=self.specific_to_excel(command), width=20)
            button.grid(row=row, column=col, padx=5, pady=5)
            self.buttons_widgets.append(button)

        # Status label at the bottom.
        self.status_label = Label(self.root, text="", bd=1)
        self.status_label.pack(side=BOTTOM, fill=X)

        self.threads = []

        # Handle closing event.
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def specific_to_excel(self, func):
        def wrapper():
            # Update status .
            self.status_label.config(text="Fetching data, please wait...", fg="blue")

            # Loading window.
            loading_window = Toplevel(self.root)
            loading_window.geometry('250x90')
            loading_window.title("Fetching...")
            Label(loading_window, text="Fetching data, please wait...").pack(padx=20, pady=10)
            Label(loading_window, text="Warning: Excel file will be overwritten.").pack(padx=20, pady=2)
            Label(loading_window, text="Please don't close this window.").pack(padx=20, pady=2)
            loading_window.grab_set()
            loading_window.resizable(False, False)

            for button in self.buttons_widgets:
                button.config(state=DISABLED)

            def task():
                try:
                    func()
                    # Close loading and show success message.
                    if not self.root_destroyed: 
                        loading_window.destroy()
                        messagebox.showinfo("Success", "Data fetched successfully! Data has been exported to your documents folder.")
                except Exception as e:
                    if not self.root_destroyed:  
                        loading_window.destroy()
                        if isinstance(e, PermissionError):
                            messagebox.showerror("Error", "Please close any open Excel files and try again.")
                        else:
                            messagebox.showerror("Error", f"An error occurred: {str(e)}. Please contact jfhhamilton@gmail.com.")
                finally:
                    if not self.root_destroyed:
                        for button in self.buttons_widgets:
                            button.config(state=NORMAL)
                    
                        self.status_label.config(text="")

            thread = threading.Thread(target=task, daemon=True) 
            thread.start()
            self.threads.append(thread) 

        return wrapper

    def on_closing(self):
        self.root_destroyed = True
        self.root.destroy()

if __name__ == "__main__":
    print("*** Welcome to ACHIEVE Web Scraper! ***")
    print("*** Keep this window open if you want to view scraping progress. ***")

    root = Tk()
    app = Application(root)
    root.mainloop()
    