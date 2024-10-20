from Window import *  # Import all components and classes from the Window module

# Initialise the main application window for the text editor
TextEditor = Window()

# Configure the main text box widget to expand and fill the available space in the window.
# This ensures that the text box dynamically resizes with the window.
TextEditor.TextBox.pack(expand=1, fill="both")

# Set up the protocol for handling the window close event (clicking the close button).
# This calls the on_closing method from the Window class to manage unsaved changes before exiting.
TextEditor.window.protocol("WM_DELETE_WINDOW", TextEditor.on_closing)

# Bind all key events in the text box to the key_pressed method.
# This allows the application to respond to keyboard inputs for text editing, shortcuts, and navigation.
TextEditor.window.bind("<Key>", TextEditor.key_pressed)

# Enter the main event loop to keep the application running and responsive.
# This loop listens for events such as keystrokes, window resizing, and close events.
TextEditor.window.mainloop()
