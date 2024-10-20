import pronouncing
import threading
import os
from nltk.corpus import words, brown
from collections import defaultdict, Counter
from tkinter import *
from tkinter import messagebox as message
from tkinter import filedialog as fd
from Stack import *


# The Window class manages all operations within the text editor, including file handling,
# text manipulation, and displaying rhymes for selected or last-typed words.
class Window:
    def __init__(self):
        # Initialization of state variables for file and editor settings
        self.isFileOpen = True  # Tracks whether a file is currently open
        self.File = ""  # Stores the path of the currently opened file
        self.isFileChange = False  # Indicates if the file has been modified
        self.elecnt = 0  # Counter for changes made in the text
        self.mode = "normal"  # Tracks the current display mode (normal/dark)
        self.fileTypes = [('All Files', '*.*'), ('Python Files', '*.py'), ('Text Document', '*.txt')]

        # Setting up the main application window
        self.window = Tk()
        self.window.geometry("1200x700+200+150")  # Window size and position
        img = PhotoImage(file='./writing.png')  # Set the window icon
        self.window.iconphoto(False, img)
        self.app_name = "Lyric Editor"  # Application name for the title
        self.File = "Untitled"  # Default file name when no file is opened
        # Set the initial window title
        self.update_title(os.path.basename(self.File))

        # Initializing the main text widget for the text editor
        self.TextBox = Text(self.window, highlightthickness=0, font=("Helvetica", 14))

        # Creating the menu bar and configuring various menus (File, Edit, View, Help)
        self.menuBar = Menu(self.window, bg="#eeeeee", font=("Helvetica", 13), borderwidth=0)
        self.window.config(menu=self.menuBar)

        # File Menu: for file operations like New, Open, Save, and Exit
        self.fileMenu = Menu(self.menuBar, tearoff=0, activebackground="#d5d5e2", bg="#eeeeee", bd=2, font="Helvetica")
        self.fileMenu.add_command(label="    New       Ctrl+N", command=self.new_file)
        self.fileMenu.add_command(label="    Open...      Ctrl+O", command=self.open_file)
        self.fileMenu.add_command(label="    Save         Ctrl+S", command=self.retrieve_input)
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label="    Exit          Ctrl+D", command=self._quit)
        self.menuBar.add_cascade(label="   File   ", menu=self.fileMenu)

        # Edit Menu: for text editing operations like Undo, Redo, Cut, Copy, and Paste
        self.editMenu = Menu(self.menuBar, tearoff=0, activebackground="#d5d5e2", bg="#eeeeee", bd=2, font="Helvetica")
        self.editMenu.add_command(label="    Undo    Ctrl+Z", command=self.undo)
        self.editMenu.add_command(label="    Redo    Ctrl+Shift+Z", command=self.redo)
        self.editMenu.add_separator()
        self.editMenu.add_command(label="    Cut    Ctrl+X", command=self.cut)
        self.editMenu.add_command(label="    Copy    Ctrl+C", command=self.copy)
        self.editMenu.add_command(label="    Paste   Ctrl+V", command=self.paste)
        self.menuBar.add_cascade(label="   Edit   ", menu=self.editMenu)

        # View Menu: for changing editor modes like dark mode
        self.viewMenu = Menu(self.menuBar, tearoff=0, activebackground="#d5d5e2", bg="#eeeeee", bd=2, font="Helvetica")
        self.viewMenu.add_command(label="   Change Mode   ", command=self.change_color)
        self.menuBar.add_cascade(label="   View   ", menu=self.viewMenu)

        # Initializing undo and redo stacks to track text changes for undo/redo functionality
        self.UStack = Stack(self.TextBox.get("1.0", "end-1c"))
        self.RStack = Stack(self.TextBox.get("1.0", "end-1c"))

        # Adding the main frame to organize the text box and rhyme panel side by side
        self.mainFrame = Frame(self.window)
        self.mainFrame.pack(fill=BOTH, expand=True)

        # Setting up the main text widget within the frame
        self.TextBox = Text(
            self.mainFrame,
            highlightthickness=0,
            font=("Helvetica", 14),
            wrap=WORD,
            padx=10,  # Horizontal padding inside the TextBox
            pady=10   # Vertical padding inside the TextBox
        )
        self.TextBox.pack(side=LEFT, fill=BOTH, expand=True, padx=20, pady=20)

        # Adding a side panel to display rhymes for the last word typed
        self.rhymePanel = Text(
            self.mainFrame,
            width=30,
            state=DISABLED,
            wrap=WORD,
            padx=5,  # Horizontal padding inside the TextBox
            pady=5   # Vertical padding inside the TextBox
            )
        self.rhymePanel.pack(side=RIGHT, fill=BOTH, expand=True, padx=20, pady=20)

        # Binding key events to detect when the user types a space, return, or punctuation, triggering rhyme lookup
        self.TextBox.bind("<space>", lambda event: self.update_rhyme_for_last_word())
        self.TextBox.bind("<Key-Return>", lambda event: self.update_rhyme_for_last_word())
        self.TextBox.bind("<Key-period>", lambda event: self.update_rhyme_for_last_word())
        self.TextBox.bind("<Control-Key-L>", lambda event: self.update_rhyme_for_last_word_previous_line())
        self.TextBox.bind("<Key-F4>", lambda event: self.update_rhyme_for_selected_word())

        # Caching common English words and word frequencies for performance optimization in rhyme lookup
        self.common_words = set(words.words())
        self.word_freq = Counter(brown.words())

    # Method to create a new file; resets the editor state
    def new_file(self):
        # Check if there are unsaved changes before creating a new file
        if self.isFileChange:
            result = message.askquestion('Save Changes', 'Do you want to save changes before creating a new file?')
            if result == "yes":
                self.save_file()  # Save the current file

        # Clear the text area and reset the editor state
        self.TextBox.config(state=NORMAL)  # Ensure the editor is editable
        self.TextBox.delete('1.0', END)  # Clear all text in the editor

        # Reset file information
        self.File = "Untitled"
        self.isFileOpen = True
        self.isFileChange = False  # Reset the change flag as there's no unsaved change now

        # Update the window title to reflect the new state
        self.update_title(self.File)

        # Reset the undo stack to start from the new blank state
        self.UStack.clear_stack()
        self.UStack.add(self.TextBox.get("1.0", "end-1c"))

    # Method to update the window title with the current filename
    def update_title(self, filename):
        # Update the window title to display the application name and current filename
        self.window.wm_title(f"{self.app_name} - {filename}")

    # Method to open an existing file and load its contents into the editor
    def open_file(self):
        self.TextBox.config(state=NORMAL)
        if self.isFileOpen and self.isFileChange:
            result = message.askquestion('Save Changes', 'Do you want to save changes before opening a new file?')
            if result == "yes":
                self.save_file()

        filename = fd.askopenfilename(filetypes=self.fileTypes, defaultextension=".txt")
        if len(filename) != 0:
            self.isFileChange = False
            with open(filename, "r") as outfile:
                text = outfile.read()
                self.TextBox.delete('1.0', END)
                self.TextBox.insert(END, text)
                self.isFileOpen = True
                self.File = filename
                self.update_title(os.path.basename(self.File))

        # Update the undo stack with the new file's content
        if self.UStack.size() > 0:
            self.UStack.clear_stack()
            self.UStack.add(self.TextBox.get("1.0", "end-1c"))

    # Method to save the currently open file or prompt to save as a new file if necessary
    def save_file(self):
        # Check if the file is "Untitled" (meaning it's a new file that hasn't been saved before)
        if self.File == "Untitled" or not self.File:
            # Prompt the user to select a location and filename for saving the file
            saveFile = fd.asksaveasfilename(filetypes=self.fileTypes, defaultextension=".txt")
            if saveFile:
                # Update the file name and write the file content
                self.File = saveFile
                self.write_file(self.File)  # Save the file content
                self.update_title(os.path.basename(self.File))  # Update the window title
        else:
            # If the file has already been saved before, simply overwrite the existing file
            self.write_file(self.File)

    # Method to write the content to the specified file
    def write_file(self, file):
        inputValue = self.TextBox.get("1.0", "end-1c")  # Get all the text in the TextBox
        with open(file, "w") as outfile:
            outfile.write(inputValue)
        self.isFileChange = False  # Reset the change flag after saving

    # Method to save the current file content if it is already open
    def retrieve_input(self):
        if self.isFileOpen and len(self.File) > 0 and self.File != "Untitled":
            # Save to the existing file
            self.write_file(self.File)
            self.isFileChange = False
        else:
            # Save as a new file
            self.save_file()
            self.isFileOpen = True

    # Key press event handler for various shortcuts and typing actions
    def key_pressed(self, event):
        # Handling shortcuts for undo, redo, save, open, and new file
        if event.char == "\x1a" and event.keysym == "Z":
            self.redo()
        elif event.char == "\x1a" and event.keysym == "z":
            self.undo()
        elif event.char == "\x13":
            self.retrieve_input()
        elif event.char == "\x0f":
            self.open_file()
        elif event.char == "\x0e":
            self.new_file()
        elif event.char == "\x04":
            self._quit()
        # Updating file change state on space or punctuation
        elif event.char in [" ", "."]:
            self.isFileChange = True
            self.UStack.add(self.TextBox.get("1.0", "end-1c"))
        # Additional handling for backspace and arrow keys
        elif event.keysym in ['Return', 'BackSpace', 'Up', 'Down', 'Left', 'Right']:
            self.isFileChange = True
            self.UStack.add(self.TextBox.get("1.0", "end-1c"))
        else:
            self.isFileChange = True
            self.UStack.add(self.TextBox.get("1.0", "end-1c"))

    # Method to undo the last change
    def undo(self):
        self.isFileChange = True
        if self.UStack.size() > 1:
            self.RStack.add(self.UStack.remove())
            text = self.UStack.peek()
            self.TextBox.delete('1.0', END)
            self.TextBox.insert(END, text)

    # Method to redo the last undone change
    def redo(self):
        if self.RStack.size() > 0:
            text = self.RStack.peek()
            self.TextBox.delete('1.0', END)
            self.TextBox.insert(END, text)
            self.UStack.add(text)
            self.RStack.remove()

    # Method to handle window close event safely
    def on_closing(self):
        if self.isFileOpen and self.isFileChange:
            result = message.askquestion('Save Changes', 'Do you want to save changes before closing?')
            if result == "yes":
                self.save_file()
        self._quit()

    # Method to quit the application and destroy the window
    def _quit(self):
        self.window.quit()
        self.window.destroy()

    # Method to toggle between normal and dark modes
    def change_color(self):
    # Toggle between 'light' and 'dark' modes
        if self.mode == "normal":
            self.mode = "dark"
            # Apply dark theme settings
            self.TextBox.configure(
                background="#1e1e1e",   # Dark gray background
                foreground="#dcdcdc",   # Light gray text
                insertbackground="#dcdcdc"  # Light gray cursor
            )
            self.rhymePanel.configure(
                background="#1e1e1e",   # Match rhyme panel background to TextBox
                foreground="#dcdcdc"    # Match text color
            )
            self.mainFrame.configure(background="#2e2e2e")  # Darker frame background
            self.window.configure(background="#2e2e2e")  # Darker window background

            # Note: Menu colors are set by the OS and may not be customizable in tkinter.
            # If you want to style menus, consider using ttk or a custom menu implementation.
        else:
            self.mode = "normal"
            # Apply light theme settings
            self.TextBox.configure(
                background="#ffffff",   # White background
                foreground="#000000",   # Black text
                insertbackground="#000000"  # Black cursor
            )
            self.rhymePanel.configure(
                background="#f0f0f0",   # Light gray background
                foreground="#000000"    # Black text
            )
            self.mainFrame.configure(background="#ffffff")  # Light frame background
            self.window.configure(background="#ffffff")  # Light window background


    # Method to copy selected text to the clipboard
    def copy(self):
        self.TextBox.clipboard_clear()
        text = self.TextBox.get("sel.first", "sel.last")
        self.TextBox.clipboard_append(text)

    # Method to cut selected text (copy + delete)
    def cut(self):
        self.copy()
        self.TextBox.delete("sel.first", "sel.last")
        self.UStack.add(self.TextBox.get("1.0", "end-1c"))

    # Method to paste text from the clipboard
    def paste(self):
        text = self.TextBox.selection_get(selection='CLIPBOARD')
        self.TextBox.insert('insert', text)
        self.UStack.add(self.TextBox.get("1.0", "end-1c"))

    # Method to update the rhyme suggestion for the last word typed
    def update_rhyme_for_last_word(self):
        full_text = self.TextBox.get("1.0", "end-1c")
        words = full_text.split()
        if words:
            last_word = words[-1]
            self.suggest_rhymes_threaded(last_word)

    def update_rhyme_for_selected_word(self):
        try:
            # Get the selected text from the TextBox
            selected_word = self.TextBox.get("sel.first", "sel.last").strip()
            # Ensure there's a selection and it's not just whitespace
            if selected_word:
                self.suggest_rhymes_threaded(selected_word)
        except TclError:
            # If no text is selected, do nothing (TclError is raised when there's no selection)
            pass

    def update_rhyme_for_last_word_previous_line(self):
        # Get the current cursor position in the TextBox
        cursor_index = self.TextBox.index(INSERT)
        # Extract the line number from the cursor position
        current_line_number = int(cursor_index.split('.')[0])

        # If the current line is greater than 1 (to ensure there's a previous line)
        if current_line_number > 1:
            # Get the content of the previous line
            previous_line_content = self.TextBox.get(f"{current_line_number - 1}.0", f"{current_line_number - 1}.end").strip()

            # Split the previous line into words and get the last word if it exists
            words = previous_line_content.split()
            if words:
                last_word = words[-1]
                self.suggest_rhymes_threaded(last_word)

    # Method to run rhyme suggestion in a separate thread for non-blocking UI updates
    def suggest_rhymes_threaded(self, word):
        thread = threading.Thread(target=self.suggest_rhymes, args=(word,))
        thread.start()

    # Method to find rhymes and update the side panel with results
    def suggest_rhymes(self, word):
        rhymes = pronouncing.rhymes(word)
        if rhymes:
            filtered_rhymes = [rhyme for rhyme in rhymes if rhyme in self.common_words]
            rhymes_by_syllable = defaultdict(list)
            for rhyme in filtered_rhymes:
                phones = pronouncing.phones_for_word(rhyme)
                if phones:
                    syllable_count = pronouncing.syllable_count(phones[0])
                    rhymes_by_syllable[syllable_count].append((rhyme, self.word_freq[rhyme]))

            rhyme_text = f"Rhymes for '{word}':\n"
            for syllable_count in sorted(rhymes_by_syllable):
                sorted_rhymes = sorted(rhymes_by_syllable[syllable_count], key=lambda x: x[1], reverse=True)
                rhyme_text += f"\n{syllable_count} Syllable{'s' if syllable_count > 1 else ''}:\n"
                rhyme_text += ", ".join([rhyme[0] for rhyme in sorted_rhymes])
        else:
            rhyme_text = f"No English rhymes found for '{word}'."

        # Update the rhymePanel using tkinter's `after` method to ensure thread-safe access
        self.window.after(0, self.update_rhyme_panel, rhyme_text)

    # Method to update the rhyme panel safely from another thread
    def update_rhyme_panel(self, rhyme_text):
        self.rhymePanel.config(state=NORMAL)
        self.rhymePanel.delete("1.0", END)
        self.rhymePanel.insert(END, rhyme_text)
        self.rhymePanel.config(state=DISABLED)
