import customtkinter as ctk
from tkinter import *
from PIL import Image
import requests
import os

ctk.set_default_color_theme('blue')
appWidth, appHeight = 650, 400
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

        self.nav_frame = NavigationFrame(self, home_frame=self.home_frame, history_frame=self.history_frame,
                                         corner_radius=0, )
        self.nav_frame.grid(row=0, column=0, sticky='nsew')

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

    def home_button_event(self):
        self.select_frame_by_name('home')

    def history_button_event(self):
        self.select_frame_by_name('myurls')

    @staticmethod
    def change_appearance_mode_event(new_appearnce_mode):
        ctk.set_appearance_mode(new_appearnce_mode)


class HomeFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # Configure Home Frame Columns
        self.columnconfigure(0, weight=1)

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
                                             text_color=('gray10', 'gray90'), compound='left')
        self.link_entry_label.grid(row=1, column=0, padx=10, pady=10, sticky='w')

        self.error_entry_label = ctk.CTkLabel(self, text='The URL field is required.',
                                              font=('montserrat', 12), text_color='red', )
        self.error_entry_label.grid(row=3, column=0, padx=10, pady=(0, 10), sticky='w')

        self.shorten_link_entry_label = ctk.CTkLabel(self, text='  New Shorten URL', image=self.link_icon,
                                                     text_color=('gray10', 'gray90'), compound='left')
        self.shorten_link_entry_label.grid(row=4, column=0, padx=10, pady=10, sticky='w')

        # Create Entry Widget for Long Link
        self.long_link_entry = ctk.CTkEntry(self, placeholder_text='Enter a long link here...',
                                            font=('montserrat', 14), height=40)
        self.long_link_entry.grid(row=2, column=0, padx=10, sticky='ew')

        # Create Entry Widget for Shorten Link
        self.short_link_entry = ctk.CTkEntry(self, placeholder_text='Short URL', font=('montserrat', 14), height=40)
        self.short_link_entry.grid(row=5, column=0, padx=10, sticky='ew')

        # Create Paste Button to paste copied URL from clipboard
        self.paste_button = ctk.CTkButton(self, text='', image=self.paste_icon, width=0,
                                          fg_color='transparent', hover_color=('gray70', 'gray30'), compound='left',
                                          command=self.paste_button_event)
        self.paste_button.grid(row=2, column=1, padx=(0, 10), sticky='e')

        # Create Copy Button to copy the shortened URL to clipboard
        self.copy_button = ctk.CTkButton(self, text='', image=self.copy_icon, width=0,
                                         fg_color='transparent', hover_color=('gray70', 'gray30'), compound='left',
                                         command=self.copy_button_event)
        self.copy_button.grid(row=5, column=1, padx=(0, 10), sticky='e')

        self.shorten_button = ctk.CTkButton(self, text='Shorten URL', font=('helvetica', 18, 'bold'),
                                            corner_radius=32)
        self.shorten_button.grid(row=6, column=0, columnspan=2, padx=20, pady=20)

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


class HistoryFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # Configure History Frame Column
        self.columnconfigure(0, weight=1)

        self.frame_label = ctk.CTkLabel(self, text='No Content Yet', font=('monsterrat', 18, 'bold'),
                                        text_color=('gray10', 'gray90'))
        self.frame_label.grid(row=0, column=0, padx=20, pady=20, sticky='ew')


if __name__ == '__main__':
    Window()
