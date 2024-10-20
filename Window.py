import pronouncing
import threading
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
        self.window.wm_title("Untitled")  # Default window title

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

        # Help Menu: for displaying information about the editor
        self.helpMenu = Menu(self.menuBar, tearoff=0, activebackground="#d5d5e2", bg="#eeeeee", bd=2, font="Helvetica")
        self.helpMenu.add_command(label="    About   ", command=self.about)
        self.menuBar.add_cascade(label="   Help   ", menu=self.helpMenu)

        # Initializing undo and redo stacks to track text changes for undo/redo functionality
        self.UStack = Stack(self.TextBox.get("1.0", "end-1c"))
        self.RStack = Stack(self.TextBox.get("1.0", "end-1c"))

        # Adding the main frame to organize the text box and rhyme panel side by side
        self.mainFrame = Frame(self.window)
        self.mainFrame.pack(fill=BOTH, expand=True)

        # Setting up the main text widget within the frame
        self.TextBox = Text(self.mainFrame, highlightthickness=0, font=("Helvetica", 14), wrap=WORD)
        self.TextBox.pack(side=LEFT, fill=BOTH, expand=True)

        # Adding a side panel to display rhymes for the last word typed
        self.rhymePanel = Text(self.mainFrame, width=30, state=DISABLED, wrap=WORD, bg="#f0f0f0")
        self.rhymePanel.pack(side=RIGHT, fill=Y)

        # Binding key events to detect when the user types a space, return, or punctuation, triggering rhyme lookup
        self.TextBox.bind("<space>", lambda event: self.update_rhyme_for_last_word())
        self.TextBox.bind("<Key-Return>", lambda event: self.update_rhyme_for_last_word())
        self.TextBox.bind("<Key-period>", lambda event: self.update_rhyme_for_last_word())

        # Caching common English words and word frequencies for performance optimization in rhyme lookup
        self.common_words = set(words.words())
        self.word_freq = Counter(brown.words())

    # Method to create a new file; resets the editor state
    def new_file(self):
        # Ensure the editor is in an editable state
        self.TextBox.config(state=NORMAL)
        if self.isFileOpen:
            if len(self.File) > 0:
                if self.isFileChange:
                    self.save_file(self.File)  # Save changes before creating a new file
                self.window.wm_title("Untitled")
                self.TextBox.delete('1.0', END)  # Clear the text area
                self.File = ''
            else:
                if self.isFileChange:
                    result = message.askquestion('Window Title', 'Do You Want to Save Changes')
                    self.save_new_file(result)
                self.window.wm_title("Untitled")
                self.TextBox.delete('1.0', END)
        else:
            self.isFileOpen = True
            self.window.wm_title("Untitled")

        self.isFileChange = False  # Reset the file change flag

        # Reset undo stack to reflect the new state
        if self.UStack.size() > 0:
            self.UStack.clear_stack()
            self.UStack.add(self.TextBox.get("1.0", "end-1c"))

    # Method to open an existing file and load its contents into the editor
    def open_file(self):
        self.TextBox.config(state=NORMAL)
        if self.isFileOpen and self.isFileChange:
            self.save_file(self.File)  # Save changes before opening a new file
        filename = fd.askopenfilename(filetypes=self.fileTypes, defaultextension=".txt")
        if len(filename) != 0:
            self.isFileChange = False
            with open(filename, "r") as outfile:
                text = outfile.read()
                self.TextBox.delete('1.0', END)
                self.TextBox.insert(END, text)
                self.window.wm_title(filename)
                self.isFileOpen = True
                self.File = filename

        # Update the undo stack with the new file's content
        if self.UStack.size() > 0:
            self.UStack.clear_stack()
            self.UStack.add(self.TextBox.get("1.0", "end-1c"))

    # Method to save the currently open file or prompt to save as a new file if necessary
    def save_file(self, file):
        result = message.askquestion('Window Title', 'Do You Want to Save Changes')
        if result == "yes":
            if len(file) == 0:
                saveFile = fd.asksaveasfile(filetypes=self.fileTypes, defaultextension=".txt")
                if saveFile:
                    self.write_file(saveFile.name)
                    self.TextBox.delete('1.0', END)
            else:
                self.write_file(file)

    # Method to handle saving a new file when prompted
    def save_new_file(self, result):
        self.isFileChange = False
        if result == "yes":
            saveFile = fd.asksaveasfile(filetypes=self.fileTypes, defaultextension=".txt")
            if saveFile:
                self.write_file(saveFile.name)
                self.File = saveFile.name
        else:
            self.TextBox.delete('1.0', END)

    # Method to write data to a file
    def write_file(self, file):
        inputValue = self.TextBox.get("1.0", "end-1c")
        with open(file, "w") as outfile:
            outfile.write(inputValue)

    # Method to save the current file content if it is already open
    def retrieve_input(self):
        if self.isFileOpen and len(self.File) != 0:
            self.write_file(self.File)
            self.isFileChange = False
        else:
            self.save_new_file("yes")
            self.window.wm_title(self.File)
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
            self.save_file(self.File)
        self._quit()

    # Method to quit the application and destroy the window
    def _quit(self):
        self.window.quit()
        self.window.destroy()

    # Method to toggle between normal and dark modes
    def change_color(self):
        if self.mode == "normal":
            self.mode = "dark"
            self.TextBox.configure(background="#2f2b2b", foreground="#BDBDBD", font=("Helvetica", 14), insertbackground="white")
        else:
            self.mode = "normal"
            self.TextBox.configure(background="white", foreground="black", font=("Helvetica", 14), insertbackground="black")

    # Method to show information about the editor
    def about(self):
        with open("About.txt", "r") as outfile:
            text = outfile.read()
            self.TextBox.insert(END, text)
            self.TextBox.config(state=DISABLED)

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
