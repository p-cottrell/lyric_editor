# Class Stack is used to manage the undo and redo operations within the text editor.
# It supports adding, removing, peeking, and clearing stack elements efficiently.
class Stack:

    def __init__(self, text):
        # Initialise the stack with the initial state of the text editor content.
        # The stack always starts with the initial text state.
        self.stack = []
        self.stack.append(text)

    def add(self, dataval):
        """
        Add a new element to the stack if it's not already present.
        This helps track the editor state changes for undo/redo functionality.

        Parameters:
        dataval (str): The text state to be added to the stack.

        Returns:
        bool: True if the element was added, False if it already exists in the stack.
        """
        if dataval not in self.stack:
            self.stack.append(dataval)
            return True
        else:
            return False

    def remove(self):
        """
        Remove the most recent element from the stack.
        This simulates an 'undo' operation by returning to the previous state.

        Returns:
        str or element: Returns a message if the stack has only the initial element;
                        otherwise, removes and returns the most recent element.
        """
        if len(self.stack) <= 1:
            return "No element in the Stack"
        else:
            return self.stack.pop()

    def peek(self):
        """
        Retrieve the top element of the stack without removing it.
        Useful for checking the current state without altering the stack.

        Returns:
        element: The top element of the stack (the most recent state).
        """
        if len(self.stack) == 1:
            return self.stack[0]  # Only the initial state is present
        else:
            return self.stack[-1]  # Return the most recent element

    def print_all(self):
        """
        Print all elements in the stack from the most recent to the oldest.
        Useful for debugging and visualising the state history.
        """
        length = len(self.stack) - 1
        while self.stack:
            print(self.stack[length])
            length -= 1

    def size(self):
        """
        Get the size of the stack.

        Returns:
        int: The number of elements currently in the stack.
        """
        return len(self.stack)

    def clear_stack(self):
        """
        Clear all elements from the stack.
        This resets the stack, removing all saved states.
        """
        return self.stack.clear()

    def ele(self, index):
        """
        Retrieve a specific element from the stack based on the index.
        Allows access to any historical state in the stack.

        Parameters:
        index (int): The index of the element to retrieve.

        Returns:
        element: The element at the specified index.
        """
        return self.stack[index]
