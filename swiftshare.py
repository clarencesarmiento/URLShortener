from datetime import datetime
from tkinter import *
from tkinter import filedialog, messagebox
from urllib.parse import urlparse
import customtkinter as ctk
import os
import qrcode
import requests
import threading
import webbrowser
from PIL import Image

ctk.set_default_color_theme('blue')
appWidth, appHeight = 650, 450
current_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Assets')


class Window(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.geometry(f'{appWidth}x{appHeight}')
        self.resizable(False, False)
        self.title('SwiftShare')
        self.iconbitmap('Assets/url-icon.ico')

        # Configure Window Column
        self.columnconfigure(1, weight=1)
        # Configure Window Row
        self.rowconfigure(0, weight=1)

        # Create Frame Objects
        self.home_frame = HomeFrame(self, corner_radius=0, fg_color=('#dee2e6', '#343a40'))

        self.history_frame = HistoryFrame(self, corner_radius=0, fg_color=('#dee2e6', '#343a40'))

        self.home_frame.history_frame = self.history_frame
        self.history_frame.home_frame = self.home_frame

        self.nav_frame = NavigationFrame(self, home_frame=self.home_frame, history_frame=self.history_frame,
                                         corner_radius=0, )
        self.nav_frame.grid(row=0, column=0, sticky='nsew')

        # Run the Application
        self.mainloop()


class NavigationFrame(ctk.CTkFrame):
    def __init__(self, master, home_frame, history_frame, **kwargs):
        super().__init__(master, **kwargs)
        # Initialize Frames
        self.home_frame = home_frame
        self.history_frame = history_frame

        # Configure Navigation Frame Row
        self.rowconfigure(3, weight=1)

        # Load and insert icon
        self.icon = ctk.CTkImage(Image.open(os.path.join(current_path, 'url-icon.png')),
                                 size=(40, 40))
        self.home_icon = ctk.CTkImage(light_image=Image.open(os.path.join(current_path, 'home-dark.png')),
                                      dark_image=Image.open(os.path.join(current_path, 'home-light.png')),
                                      size=(20, 20))
        self.history_icon = ctk.CTkImage(light_image=Image.open(os.path.join(current_path, 'history-dark.png')),
                                         dark_image=Image.open(os.path.join(current_path, 'history-light.png')),
                                         size=(20, 20))

        # Create title in Navigation Frame
        self.nav_title_label = ctk.CTkLabel(self, text='  SwiftShare', font=('helvetica', 20, 'bold'),
                                            image=self.icon, compound='left')
        self.nav_title_label.grid(row=0, column=0, padx=20, pady=20)

        self.nav_desc_label = ctk.CTkLabel(self, text='Powered by: TinyURL', font=('helvetica', 10, 'bold'))
        self.nav_desc_label.grid(row=7, column=0, padx=20, pady=10, sticky='s')

        # Create Buttons
        self.home_button = ctk.CTkButton(self, text='Home', image=self.home_icon,
                                         text_color=('gray10', 'gray90'), hover_color=('gray70', 'gray30'),
                                         fg_color='transparent', anchor='w', corner_radius=0, height=40,
                                         border_spacing=10, command=self.home_button_event)
        self.home_button.grid(row=1, column=0, sticky='ew')

        self.history_button = ctk.CTkButton(self, text='My URLs', image=self.history_icon,
                                            text_color=('gray10', 'gray90'), hover_color=('gray70', 'gray30'),
                                            fg_color='transparent', anchor='w', corner_radius=0, height=40,
                                            border_spacing=10, command=self.history_button_event)
        self.history_button.grid(row=2, column=0, sticky='ew')

        self.appearance_mode_menu = ctk.CTkOptionMenu(self, values=['System', 'Light', 'Dark'],
                                                      command=self.change_appearance_mode_event)
        self.appearance_mode_menu.grid(row=6, column=0, padx=20, sticky='s')

        # Set default Frame
        self.select_frame_by_name('home')

    def select_frame_by_name(self, name):
        self.home_button.configure(fg_color=('gray75', 'gray25') if name == 'home' else 'transparent')
        self.history_button.configure(fg_color=('gray75', 'gray25') if name == 'myurls' else 'transparent')

        # Show selected frame
        if name == 'home':
            self.home_frame.grid(row=0, column=1, sticky='nsew')
        else:
            self.home_frame.grid_forget()

        if name == 'myurls':
            self.history_frame.grid(row=0, column=1, sticky='nsew')
        else:
            self.history_frame.grid_forget()

    # Create a Home Button Event Function
    def home_button_event(self):
        self.select_frame_by_name('home')

    # Create a History Button Event Function
    def history_button_event(self):
        self.select_frame_by_name('myurls')

    # Create a Change Appearance Mode Event Function
    @staticmethod
    def change_appearance_mode_event(new_appearnce_mode):
        ctk.set_appearance_mode(new_appearnce_mode)


class HomeFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.toplevel_window = None
        self.history_frame = None
        self.short_url_list = []

        # Configure Home Frame Columns
        self.columnconfigure(0, weight=1)

        # Configure Home Frame Row
        self.rowconfigure(7, weight=1)

        # Load and Insert Icons
        self.link_icon = ctk.CTkImage(light_image=Image.open(os.path.join(current_path, 'link-dark.png')),
                                      dark_image=Image.open(os.path.join(current_path, 'link-light.png')),
                                      size=(20, 20))
        self.paste_icon = ctk.CTkImage(light_image=Image.open(os.path.join(current_path, 'paste-dark.png')),
                                       dark_image=Image.open(os.path.join(current_path, 'paste-light.png')),
                                       size=(20, 20))
        self.copy_icon = ctk.CTkImage(light_image=Image.open(os.path.join(current_path, 'copy-dark.png')),
                                      dark_image=Image.open(os.path.join(current_path, 'copy-light.png')),
                                      size=(20, 20))

        # Create a Description for Home Frame
        description_text = 'Share in a heartbeat.\nShorten your URLs swiftly and share them effortlessly.\nExperience the joy of instant link sharing with SwiftShare.'
        self.frame_desc_label = ctk.CTkLabel(self, text=description_text, font=('montserrat', 14, 'italic'),
                                             text_color=('gray10', 'gray90'), justify='center')
        self.frame_desc_label.grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky='ew')

        # Create labels
        self.link_entry_label = ctk.CTkLabel(self, text='  Insert a long URL', image=self.link_icon,
                                             font=('montserrat', 14), text_color=('gray10', 'gray90'),
                                             compound='left')
        self.link_entry_label.grid(row=1, column=0, padx=10, pady=10, sticky='w')

        self.error_entry_label = ctk.CTkLabel(self, text='', font=('montserrat', 12), text_color='#D80032', )
        self.error_entry_label.grid(row=3, column=0, padx=10, pady=(0, 10), sticky='w')

        self.shorten_link_entry_label = ctk.CTkLabel(self, text='  New Shorten URL', image=self.link_icon,
                                                     font=('montserrat', 14), text_color=('gray10', 'gray90'),
                                                     compound='left')
        self.shorten_link_entry_label.grid(row=4, column=0, padx=10, pady=10, sticky='w')

        self.error_qrcode_label = ctk.CTkLabel(self, text='', font=('montserrat', 12), text_color='#D80032', )
        self.error_qrcode_label.grid(row=6, column=0, padx=10, pady=(0, 10), sticky='w')

        self.github_label = ctk.CTkLabel(self, text='Made with ❤ by Clarence Sarmiento', cursor='hand2',
                                         font=('montserrat', 12, 'underline'), text_color="#068FFF")
        self.github_label.grid(row=8, column=0, columnspan=2, padx=10, pady=10, sticky='ew')
        self.github_label.bind('<Button-1>', lambda event: self.open_github_link())

        # Create Entry Widget for Long Link
        self.long_link_entry = ctk.CTkEntry(self, placeholder_text='Enter a long link here...',
                                            font=('montserrat', 14), height=40, )
        self.long_link_entry.grid(row=2, column=0, padx=10, sticky='ew')

        # Create Entry Widget for Shorten Link
        self.short_link_entry = ctk.CTkEntry(self, placeholder_text='Short URL', font=('montserrat', 14), height=40)
        self.short_link_entry.grid(row=5, column=0, padx=10, sticky='ew')

        # Create Paste Button to paste copied URL from clipboard
        self.paste_button = ctk.CTkButton(self, text='', image=self.paste_icon, width=0,
                                          fg_color='transparent', hover_color=('gray70', 'gray30'),
                                          command=self.paste_button_event)
        self.paste_button.grid(row=2, column=1, padx=(0, 10), sticky='e')

        # Create Copy Button to copy the shortened URL to clipboard
        self.copy_button = ctk.CTkButton(self, text='', image=self.copy_icon, width=0,
                                         fg_color='transparent', hover_color=('gray70', 'gray30'),
                                         command=self.copy_button_event)
        self.copy_button.grid(row=5, column=1, padx=(0, 10), sticky='e')

        # Create Shorten Button
        self.shorten_button = ctk.CTkButton(self, text='Shorten URL', font=('helvetica', 12, 'bold'),
                                            corner_radius=32, command=self.on_click_shorten_button)
        self.shorten_button.grid(row=3, column=0, columnspan=2, padx=(0, 10), pady=10, sticky='e')

        # Create Button to Generate QR code for the shortened URL
        self.gen_qrcode_button = ctk.CTkButton(self, text='QR Code', font=('helvetica', 12, 'bold'), corner_radius=32,
                                               command=self.gen_qrcode_button_event)
        self.gen_qrcode_button.grid(row=6, column=0, columnspan=2, padx=(0, 10), pady=10, sticky='e')

    # Create a Paste Button Function
    def paste_button_event(self):
        # Get the text from the clipboard
        pasted_text = self.clipboard_get()

        # Insert the text into the Long Link Entry Widget
        self.long_link_entry.delete(0, 'end')
        self.long_link_entry.insert(0, pasted_text)

    # Create a Copy Button Function
    def copy_button_event(self):
        # Get the text from the Entry widget
        copied_text = self.short_link_entry.get()

        # Put the text in the clipboard
        self.clipboard_clear()
        self.clipboard_append(copied_text)
        self.update()

    # Let's Validate first the long link entry widget entry
    def has_input_and_valid(self, url):
        if url:
            parsed_url = urlparse(url)
            if parsed_url.scheme and parsed_url.netloc:
                try:
                    checked_url_status = requests.get(url)
                    if checked_url_status.status_code == 200:
                        self.error_entry_label.configure(text='')
                        self.long_link_entry.configure(border_color=('#979DA2', '#565B5E'))
                        return True
                    else:
                        self.error_entry_label.configure(text=f'HTTP Status Code: {checked_url_status.status_code}.')
                        self.long_link_entry.configure(border_color='red')
                except requests.RequestException:
                    self.error_entry_label.configure(text='Invalid URL.')
                    self.long_link_entry.configure(border_color='red')
            else:
                self.error_entry_label.configure(text='Should have https://')
                self.long_link_entry.configure(border_color='red')
        else:
            self.error_entry_label.configure(text='The URL field is required.')
            self.long_link_entry.configure(border_color='red')
        return False

    # Create a Shorten Button Function
    def shorten_button_event(self):
        base_url = 'http://tinyurl.com/api-create.php?url='
        url_to_shorten = self.long_link_entry.get().strip()
        if self.has_input_and_valid(url_to_shorten):
            response = requests.get(base_url + url_to_shorten)
            self.short_link_entry.configure(state='normal')
            self.short_link_entry.delete(0, 'end')
            self.short_link_entry.insert(0, response.text)
            self.short_link_entry.configure(state='disable')
            if response.text not in self.short_url_list:
                self.history_frame.add_item_frame(url_name=urlparse(url_to_shorten).netloc, url_short=response.text)
                self.short_url_list.append(response.text)
        return

    def on_click_shorten_button(self):
        thread = threading.Thread(target=self.shorten_button_event)
        thread.start()

    # Create Generate QRCode Button Function
    def gen_qrcode_button_event(self):
        data = self.short_link_entry.get()
        if not data:
            self.error_qrcode_label.configure(text='No data to generate to QRCode.')
            return

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=2,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        qr_img = ctk.CTkImage(img.get_image(), size=(256, 256))

        # Display the generated QRcode in another window
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = QRCodeWindow(self, qr_ctkimage=qr_img, raw_image=img)
        else:
            self.toplevel_window.focus()

    # Create a clickable link for gitHub
    @staticmethod
    def open_github_link():
        github_link = 'https://github.com/clarencesarmiento'
        webbrowser.open_new(github_link)


class HistoryFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.home_frame = None
        self.frame_list = []

        # Configure History Frame Column
        self.columnconfigure(0, weight=1)

        # Configure History Frame Row
        self.rowconfigure(1, weight=1)

        # Create Frame Label
        self.frame_label = ctk.CTkLabel(self, text='My URLs', font=('monsterrat', 18, 'bold'),
                                        text_color=('gray10', 'gray90'))
        self.frame_label.grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky='ew')

        # Create a Scrollable Frame to store the recent shortened urls
        self.scrollable_frame = ctk.CTkScrollableFrame(self)
        self.scrollable_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 10), sticky='nsew')
        self.scrollable_frame.columnconfigure(0, weight=1)

        # Create a Label inside the scrollable frame
        self.no_url_label = ctk.CTkLabel(self.scrollable_frame, text='No recent URLs in your History',
                                         font=('monsterrat', 16, 'bold'))
        self.no_url_label.grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky='ew')

    # A function to add a frame in the scrollable frame which contains details
    def add_item_frame(self, url_name, url_short):
        copy_icon = ctk.CTkImage(light_image=Image.open(os.path.join(current_path, 'copy-dark.png')),
                                 dark_image=Image.open(os.path.join(current_path, 'copy-light.png')),
                                 size=(20, 20))

        qrcode_icon = ctk.CTkImage(light_image=Image.open(os.path.join(current_path, 'qrcode-dark.png')),
                                   dark_image=Image.open(os.path.join(current_path, 'qrcode-light.png')),
                                   size=(20, 20))

        delete_icon = ctk.CTkImage(light_image=Image.open(os.path.join(current_path, 'trash-dark.png')),
                                   dark_image=Image.open(os.path.join(current_path, 'trash-light.png')),
                                   size=(20, 20))

        current_time = datetime.now().time()
        formatted_time = current_time.strftime('%I:%M %p')

        # Create a Frame that will hold all the information
        frame = ctk.CTkFrame(self.scrollable_frame, fg_color='#228be6', )
        frame.columnconfigure(0, weight=1)
        frame.grid(row=len(self.frame_list), column=0, pady=(0, 10), sticky='ew')

        # Display the URL Netloc
        url_name_label = ctk.CTkLabel(frame, text=f'{url_name}', font=('monsterrat', 16, 'bold'),
                                      text_color=('gray10', 'gray90'),)
        url_name_label.grid(row=0, column=0, padx=10, pady=10, sticky='w')

        # Display Time the url was shortened
        time_label = ctk.CTkLabel(frame, text=f'{formatted_time}', font=('monsterrat', 12),
                                  text_color=('gray10', 'gray90'))
        time_label.grid(row=0, column=1, columnspan=2, padx=10, pady=10, sticky='e')

        # Display the shortened URL
        url_short_label = ctk.CTkLabel(frame, text=f'{url_short}', font=('monsterrat', 14),
                                       text_color=('gray10', 'gray90'))
        url_short_label.grid(row=1, column=0, padx=10, pady=(0, 10), sticky='w')

        # Create a copy button to copy the shortened url
        copy_button = ctk.CTkButton(frame, text='', image=copy_icon, width=0,
                                    fg_color='transparent', hover_color=('gray70', 'gray30'),
                                    command=lambda: self.copy_button_event(url_short_label))
        copy_button.grid(row=1, column=0, padx=10, pady=(0, 10), sticky='e')

        # Create a qr button to generate qrcode
        qr_button = ctk.CTkButton(frame, text='', image=qrcode_icon, width=0,
                                  fg_color='transparent', hover_color=('gray70', 'gray30'),
                                  command=lambda: self.qr_button_event(url_short_label))
        qr_button.grid(row=1, column=1, padx=(0, 10), pady=(0, 10), sticky='e')

        # Create a delete button to remove the entire frame
        delete_button = ctk.CTkButton(frame, text='', image=delete_icon, width=0,
                                      fg_color='#fa5252', hover_color='#e03131',
                                      command=lambda: self.delete_button_event(frame))
        delete_button.grid(row=1, column=2, padx=(0, 10), pady=(0, 10), sticky='w')

        self.frame_list.append({'frame': frame, 'short_url': url_short_label})
        self.update_scrollable_frame()

    # Delete Button Function to delete the desired frame
    def delete_button_event(self, item_frame):
        for frame in self.frame_list:
            if frame['frame'] == item_frame and frame['short_url'].cget('text') in self.home_frame.short_url_list:
                item_frame.destroy()
                self.frame_list.remove(frame)
                self.home_frame.short_url_list.remove(frame['short_url'].cget('text'))
                self.update_scrollable_frame()

                break

    # Update the scrollable frame everytime an item is added or removed
    def update_scrollable_frame(self):
        # Let's remove the label if there's added item
        if len(self.frame_list) != 0:
            self.no_url_label.grid_forget()
        else:
            self.no_url_label.grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky='ew')

        # Let's update the scrollable frame and place the items in reverse order
        for i, frame in enumerate(reversed(self.frame_list)):
            frame['frame'].grid(row=i, column=0, pady=(0, 10), sticky='ew')

    # Create a Copy Button Function to integrate in every frame
    def copy_button_event(self, label):
        copied_text = label.cget('text')

        # Put the text in the clipboard
        self.clipboard_clear()
        self.clipboard_append(copied_text)
        self.update()

    # Create a QR Button Function to integrate in every frame
    def qr_button_event(self, label):
        data = label.cget('text')
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=2,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        qr_img = ctk.CTkImage(img.get_image(), size=(256, 256))

        # Display the generated QRcode in another window
        if self.home_frame.toplevel_window is None or not self.home_frame.toplevel_window.winfo_exists():
            self.home_frame.toplevel_window = QRCodeWindow(self, qr_ctkimage=qr_img, raw_image=img)
        else:
            self.home_frame.toplevel_window.destroy()
            self.qr_button_event(label)


class QRCodeWindow(ctk.CTkToplevel):
    def __init__(self, master, qr_ctkimage, raw_image, **kwargs):
        super().__init__(master, **kwargs)
        self.qr_ctkimage = qr_ctkimage
        self.raw_image = raw_image

        self.title('Generated QR Code')
        self.resizable(False, False)

        self.qrcode_image_label = ctk.CTkLabel(self, text='', image=self.qr_ctkimage)
        self.qrcode_image_label.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

        self.download_button = ctk.CTkButton(self, text='Download QR Code', font=('helvetica', 12, 'bold'),
                                             corner_radius=32, command=self.download_button_event)
        self.download_button.grid(row=1, column=0, padx=10, pady=(0, 10))

    def download_button_event(self):
        # Get the QR Code raw image
        qr_image = self.raw_image.get_image()

        # Prompt the user to choose the file path
        file_path = filedialog.asksaveasfilename(defaultextension='.png', filetypes=[('PNG files', '*.png')])

        if file_path:
            # Save the PIL Image to the specified file path
            qr_image.save(file_path)

            messagebox.showinfo(title='QR Code Saved', message='QR Code saved successfully.')


if __name__ == '__main__':
    Window()
