class MaxHeap:
    def __init__(self):
        self.heap = []

    def insert(self, book):
        self.heap.append(book)
        self._heapify_up(len(self.heap) - 1)

    def _heapify_up(self, index):
        parent_index = (index - 1) // 2
        if index > 0 and self.heap[index]['overdue_days'] > self.heap[parent_index]['overdue_days']:
            self.heap[index], self.heap[parent_index] = self.heap[parent_index], self.heap[index]
            self._heapify_up(parent_index)

    def extract_max(self):
        if not self.heap:
            return None
        if len(self.heap) == 1:
            return self.heap.pop()
        root = self.heap[0]
        self.heap[0] = self.heap.pop()
        self._heapify_down(0)
        return root

    def _heapify_down(self, index):
        largest = index
        left_index = 2 * index + 1
        right_index = 2 * index + 2

        if left_index < len(self.heap) and self.heap[left_index]['overdue_days'] > self.heap[largest]['overdue_days']:
            largest = left_index
        if right_index < len(self.heap) and self.heap[right_index]['overdue_days'] > self.heap[largest]['overdue_days']:
            largest = right_index
        if largest != index:
            self.heap[index], self.heap[largest] = self.heap[largest], self.heap[index]
            self._heapify_down(largest)

    def is_empty(self):
        return len(self.heap) == 0


class AVLNode:
    def __init__(self, book):
        self.book = book
        self.left = None
        self.right = None
        self.height = 1


class AVLTree:
    def insert(self, node, book):
        if not node:
            return AVLNode(book)
        elif book['isbn'] < node.book['isbn']:
            node.left = self.insert(node.left, book)
        else:
            node.right = self.insert(node.right, book)

        node.height = 1 + max(self.get_height(node.left), self.get_height(node.right))
        balance = self.get_balance(node)

        # Left Left Case
        if balance > 1 and book['isbn'] < node.left.book['isbn']:
            return self.rotate_right(node)

        # Right Right Case
        if balance < -1 and book['isbn'] > node.right.book['isbn']:
            return self.rotate_left(node)

        # Left Right Case
        if balance > 1 and book['isbn'] > node.left.book['isbn']:
            node.left = self.rotate_left(node.left)
            return self.rotate_right(node)

        # Right Left Case
        if balance < -1 and book['isbn'] < node.right.book['isbn']:
            node.right = self.rotate_right(node.right)
            return self.rotate_left(node)

        return node

    def delete(self, node, isbn):
        if not node:
            return node

        if isbn < node.book['isbn']:
            node.left = self.delete(node.left, isbn)
        elif isbn > node.book['isbn']:
            node.right = self.delete(node.right, isbn)
        else:
            if not node.left:
                return node.right
            elif not node.right:
                return node.left
            temp = self.get_min_value_node(node.right)
            node.book = temp.book
            node.right = self.delete(node.right, temp.book['isbn'])

        node.height = 1 + max(self.get_height(node.left), self.get_height(node.right))
        balance = self.get_balance(node)

        if balance > 1 and self.get_balance(node.left) >= 0:
            return self.rotate_right(node)
        if balance < -1 and self.get_balance(node.right) <= 0:
            return self.rotate_left(node)
        if balance > 1 and self.get_balance(node.left) < 0:
            node.left = self.rotate_left(node.left)
            return self.rotate_right(node)
        if balance < -1 and self.get_balance(node.right) > 0:
            node.right = self.rotate_right(node.right)
            return self.rotate_left(node)

        return node

    def get_min_value_node(self, node):
        current = node
        while current.left:
            current = current.left
        return current

    def rotate_left(self, z):
        y = z.right
        T2 = y.left

        y.left = z
        z.right = T2

        z.height = 1 + max(self.get_height(z.left), self.get_height(z.right))
        y.height = 1 + max(self.get_height(y.left), self.get_height(y.right))

        return y

    def rotate_right(self, z):
        y = z.left
        T3 = y.right

        y.right = z
        z.left = T3

        z.height = 1 + max(self.get_height(z.left), self.get_height(z.right))
        y.height = 1 + max(self.get_height(y.left), self.get_height(y.right))

        return y

    def get_height(self, node):
        if not node:
            return 0
        return node.height

    def get_balance(self, node):
        if not node:
            return 0
        return self.get_height(node.left) - self.get_height(node.right)


class StaticBookManager:
    def __init__(self, size):
        self.books = {}
        self.undo_stack = []
        self.max_history = 10
        self.avl_tree = None
        self.overdue_heap = MaxHeap()

    def add_book(self, title, author, isbn):
        if len(isbn) > 4 or not isbn.isdigit():
            print("ISBN must be a 4-digit number.")
            return

        if isbn not in self.books:
            book = {'title': title, 'author': author, 'isbn': isbn, 'available': True, 'overdue_days': 0}
            self.books[isbn] = book
            self.avl_tree = AVLTree().insert(self.avl_tree, book)
            self.undo_stack.append(('remove', isbn))

            if len(self.undo_stack) > self.max_history:
                self.undo_stack.pop(0)

            self.display_books()
        else:
            print("Isbn number already used.")

    def mark_overdue(self, isbn, overdue_days):
        book = self.books.get(isbn)
        if book:
            book['overdue_days'] = overdue_days
            self.overdue_heap.insert(book)
        else:
            print("Book not found.")

    def notify_overdue_books(self):
        print("\nNotifying overdue books:")
        while not self.overdue_heap.is_empty():
            overdue_book = self.overdue_heap.extract_max()
            print(f"Notify: Book '{overdue_book['title']}' is overdue by {overdue_book['overdue_days']} days.")

    def remove_book(self, isbn):
        book = self.books.pop(isbn, None)
        if book:
            self.avl_tree = AVLTree().delete(self.avl_tree, isbn)
            if book in self.overdue_heap.heap:
                self.overdue_heap.heap.remove(book)
                self._heapify_overdue_heap()
            self.undo_stack.append(('add', book))
            if len(self.undo_stack) > self.max_history:
                self.undo_stack.pop(0)
            print(f"Book with ISBN {isbn} removed successfully.")
            self.display_books()
        else:
            print("Book not found.")

    def _heapify_overdue_heap(self):
        new_heap = MaxHeap()
        for book in self.overdue_heap.heap:
            new_heap.insert(book)
        self.overdue_heap = new_heap

    def display_books(self):
        print("\nCurrent list of books:")
        for book in self.books.values():
            status = "Available" if book['available'] else "Unavailable due to borrowed"
            print(f"Title: {book['title']}, Author: {book['author']}, ISBN: {book['isbn']}, Overdue Days: {book['overdue_days']}, Status: {status}")
        print("")

    def borrow_book(self, isbn):
        book = self.books.get(isbn)
        if book and book['available']:
            book['available'] = False
            print(f"You have borrowed '{book['title']}'.")
        else:
            print("Book not available for borrowing.")

    def view_overdue_books(self):
        print("\nOverdue Books:")
        for book in self.overdue_heap.heap:
            print(f"Title: {book['title']}, Overdue Days: {book['overdue_days']}")
        print("")

    def undo(self):
        if self.undo_stack:
            action, isbn = self.undo_stack.pop()
            if action == 'add':
                self.books[isbn] = isbn  # Adjust this if necessary for your structure
                print(f"Undid: Added book '{isbn}'.")
            elif action == 'remove':
                self.books.pop(isbn, None)
                print("Undid: Removed a book.")
        else:
            print("No actions to undo.")

    def search_by_isbn(self, isbn):
        return self.books.get(isbn, None)


# Testing the StaticBookManager with Overdue Books Management
if __name__ == "__main__":
    static_manager = StaticBookManager(size=10)

    # Pre-fill with two overdue books
    static_manager.add_book("The Great Gatsby", "F. Scott Fitzgerald", "1234")
    static_manager.mark_overdue("1234", 15)  # Overdue by 15 days

    static_manager.add_book("To Kill a Mockingbird", "Harper Lee", "5678")
    static_manager.mark_overdue("5678", 10)  # Overdue by 10 days

    while True:
        action = input("\nChoose an action: [1] Manage Books [2] Borrow Books [3] Overdue Books [4] Exit: ")

        if action == '1':
            manage_action = input("\nManage Books: [1] Add Book [2] Search by ISBN [3] Remove Book [4] Undo: ")
            if manage_action == '1':
                title = input("Enter the book title: ")
                author = input("Enter the author's name: ")
                isbn = input("Enter the ISBN number (4 digits): ")
                static_manager.add_book(title, author, isbn)
            elif manage_action == '2':
                isbn_to_search = input("Enter the ISBN to search for: ")
                book = static_manager.search_by_isbn(isbn_to_search)
                if book:
                    print(f"Found book: Title: {book['title']}, Author: {book['author']}, Status: {book['available']}")
                else:
                    print("Book not found.")
            elif manage_action == '3':
                isbn_to_remove = input("Enter the ISBN of the book to remove: ")
                static_manager.remove_book(isbn_to_remove)
            elif manage_action == '4':
                static_manager.undo()
            else:
                print("Invalid option, please try again.")

        elif action == '2':
            isbn_to_borrow = input("Enter the ISBN of the book you want to borrow: ")
            static_manager.borrow_book(isbn_to_borrow)

        elif action == '3':
            static_manager.view_overdue_books()
            notify_action = input("Would you like to notify overdue books? (yes/no): ")
            if notify_action.lower() == 'yes':
                static_manager.notify_overdue_books()

        elif action == '4':
            print("Exiting the program.")
            break
        else:
            print("Invalid option, please try again.")
