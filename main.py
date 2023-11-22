from datetime import datetime
import json
from collections import Counter

class Book:
    def __init__(self, title, author, language, year, genre):
        self.title = title
        self.author = author
        self.lanlanguage = language
        self.year = year
        self.genre = genre
        self.book_id = ""
        self.loan_history = []
        self.is_available = True
    
    def __str__(self):
        return(f"\"{self.title}\", {self.author}")
# gets information from the history of all loans and returns
    def get_available_info(self, library):
        for record in library.history.values():        
            if record["book"] == self.book_id and "return_time" not in record.keys():
                self.is_available = False

class Customer:
    def __init__(self, customer_id, first_name, last_name, phone_number):
        self.first_name = first_name
        self.last_name = last_name
        self.phone_number = phone_number
        self.customer_id = customer_id
        self.loaned_books = []
        self.loan_time = []
        self.orders = []

    def __str__(self):
        return(f"{self.first_name} {self.last_name}")

# gets information about books currently borrowed by the сustomer from the history of all loans and returns
    def get_loaned_books(self, library):
        for key, value in library.history.items():
            if key.split("_")[0] == self.customer_id:
                for book in library.books:
                    if value["book"] == book.book_id and "return_time" not in value.keys():
                        self.loaned_books.append(book)
                        self.loan_time.append(value["loan_time"])

# gets information about orders of customer from the history of all orders
    def get_orders(self, library):
        for key, value in library.orders.items():
            if key.split("_")[0] == self.customer_id:
                self.orders.append(value)

# finds out if customer can borrow, return and order books
    def restrictions(self):
        action_restrictions = {"loan": False, "return": False, "order": False}
        if len(self.loaned_books) < 2:
            action_restrictions["loan"] = True
        if len(self.loaned_books) > 0:
            action_restrictions["return"] = True
        if len(self.orders) < 2:
            action_restrictions["order"] = True
        return action_restrictions

# displays books currently borrowed by the сustomer with the time of borrowing
    def display_loaned_books(self, library):
        self.loaned_books = []
        self.loan_time = []
        self.get_loaned_books(library)
        for item in zip(self.loaned_books, self.loan_time):
         print(f"{item[0]} borrowed {item[1]}")

# displays books currently ordered by the сustomer with the time of order
    def display_orders(self, library):
        self.orders = []
        self.get_orders(library)
        for order in self.orders:
         print(f"\"{order['new_book_title']}\", {order['new_book_author']} ordered {order['order_time']}")

class Library:
    def __init__(self, name, address):
        self.name = name
        self.address = address
        self.books = []
        self.customers = []
        self.employers = []
        self.history = {}
        self.orders = {}

    def add_book(self, book):
        self.books.append(book)

# reads all books of the library from file
    def add_books_from_file(self):
        try:
            books_file = open("books.json", "r")
            all_books = json.load(books_file)
            books_file.close()
            for book_dict in all_books:
                book = Book(book_dict["title"], book_dict["author"], book_dict["language"], book_dict["year"], book_dict["genre"])
                book.book_id = book_dict["book_id"]
                self.add_book(book)
        except FileNotFoundError:
            pass

    def add_customers(self, customer):
        self.customers.append(customer)

# adds customers from the file if library already has customers
    def add_customers_from_file(self, customers_file):
        try:
            customers_file = open("customers.json", "r")
            all_customers = json.load(customers_file)
            customers_file.close()
            for customer_dict in all_customers:
                customer = Customer(customer_dict["customer_id"], customer_dict["first_name"], customer_dict["last_name"], customer_dict["phone_number"])
                self.add_customers(customer)
        except FileNotFoundError:
            pass

# adds customers from keybord
# registers a new customer or reminds to the customer his id number if it already exists
    def add_customer_from_keyboard(self, action):
        first_name = self.user_input("Enter your first name: ")
        last_name = self.user_input("Enter your last name: ")
        phone_number = self.user_input("Enter your phone number without spaces or separators: ")
        if not phone_number.isnumeric():
            print("Invalid phone number format. Try again")
            phone_number = self.user_input("Enter your phone number without spaces or separators: ")
            if not phone_number.isnumeric():
                print("Invalid phone number format. Session ended")
                return
        for customer in self.customers:
            if customer.first_name == first_name.capitalize() and customer.last_name == last_name.capitalize() and customer.phone_number == phone_number:
                print(f"We have a registered customer with this data. Customer id is {customer.customer_id}")
                return
        if action == "forgot_id":
            print("Customer not found")
            print(f"Do you want to register at the library \"{self.name}\"?")
            user_answer = self.user_input("Type \"Y\" for register, \"N\" for exit: ")
            if user_answer.lower() in ["y", "yes"]:
                action = "registration"
            elif user_answer.lower() in ["n", "no"]:
                print("Session ended")                
            else:
                print("Unacceptable answer. Session ended")
        if action == "registration":
            try:
                id = int(self.customers[-1].customer_id) + 1
            except IndexError:
                id = 1
            new_customer = Customer(str(id), first_name.capitalize(), last_name.capitalize(), phone_number) 
            self.add_customers(new_customer)
            self.save_customers_file(customers_file="customers.json")
            print(f"New customer registration was successful\nId nuber of customer {new_customer} is {id}")

# finds object customer if we know his id number
    def find_customer(self, customer_id):
        for customer in self.customers:
            if customer.customer_id == customer_id:
                return customer

# finds object book if we know its id number            
    def find_book(self, book_id):
        for book in self.books:
            if book.book_id == book_id:
                return book
        
# finds out 3 most popular book from from the history of all loans and returns
# and show them on display
# there may be several identical books in the library
    def display_popular_books(self):
        popular_books = Counter(record["title"] for record in self.history.values())
        most_popular_books = popular_books.most_common(3)
        if most_popular_books:
            print("Most popular books in our library:")
            for item in most_popular_books:
                for book in self.books:
                    if item[0] == book.title:
                        print(book)
                        break

# loads history of all loans and returns from the file if it already exists                            
    def load_history(self, history_file):
        try:
            history_file = open("history.json", "r")
            history = json.load(history_file)
            history_file.close()
            self.history.update(history)
        except FileNotFoundError:
            pass

# loads history of all orders from the file if it already exists  
    def load_orders(self, orders_file):
        try:
            orders_file = open("orders.json", "r")
            orders = json.load(orders_file)
            orders_file.close()
            self.orders.update(orders)
        except FileNotFoundError:
            pass

# gets all information about loans, retuns, orders, availablty of the books, etc.
    def load_all_data(self):
        self.add_books_from_file()
        self.add_customers_from_file(customers_file="customers.json")
        self.load_history(history_file="history.json")
        self.load_orders(orders_file="orders.json")
        for book in self.books:
            book.get_available_info(self)
        for customer in self.customers:
            customer.get_loaned_books(self)
            customer.get_orders(self)

# saves history of loans and returns to the file
    def save_history(self, history_file):
        history_file = open("history.json", "w")
        json.dump(self.history, history_file, indent=2)
        history_file.close()

# saves history of orders to the file
    def save_orders(self, orders_file):
        orders_file = open("orders.json", "w")
        json.dump(self.orders, orders_file, indent=2)
        orders_file.close()

# saves new customers to the file
    def save_customers_file(self, customers_file):
        customers_file = open("customers.json", "w")
        customers = []
        for customer in self.customers:
            customers.append({"customer_id": customer.customer_id, "first_name": customer.first_name, "last_name": customer.last_name, "phone_number": customer.phone_number})
        json.dump(customers, customers_file, indent=2)
        customers_file.close()

# saves all information about loans, returns, orders and customers to the files
    def save_all_data(self):
        self.save_history(history_file="history.json")
        self.save_orders(orders_file="orders.json")
        self.save_customers_file(customers_file="customers.json")

# checks if we have a book in the library and if it is available for loan
# there may be several identical books in the library
    def check_availability_by_title(self, book_title):
        result = "not in stock"
        for book in self.books:
            if book_title.lower() == book.title.lower():
                result = "not available"
                if book.is_available:
                    result = book
                    break
                else:
                    continue
        return result

# loans book for a customer if it is available
# adds information about loan to history
    def loan_book(self, customer_id, book_title):
        current_customer = self.find_customer(customer_id)
        check = self.check_availability_by_title(book_title)
        if check == "not in stock":
            print(f"Sorry, \"{book_title}\" is out of stock. You can order it and we will add \"{book_title}\" to our library")
        elif check == "not available":
            print(f"Sorry, \"{book_title}\" is not available now\nYou can borrow another book from our library")
        else:
            book = self.check_availability_by_title(book_title)
            book.is_available = False                
            current_customer.loaned_books.append(book)
            time = datetime.now().strftime("%d.%m.%Y %H:%M")
            new_loan = {"customer": customer_id, "book": book.book_id, "title": book.title, "loan_time": time}
            all_record_numbers = [record_id.split("_") for record_id in self.history.keys()]
            new_record_number = (max((int(record_number[1]) for record_number in all_record_numbers if record_number[0] == customer_id), default=0)) + 1
            new_record_id = f"{customer_id}_{new_record_number}"
            self.history.update({new_record_id: new_loan})
            self.save_history(history_file="history.json")
            print(f"\"{book.title}\" loaned to customer {current_customer}") 
        
        self.continue_customer_session(customer_id)
    
# checks if customer has borrowed the book and return it to the library 
# adds information about return to history
    def return_book(self, customer_id, book_title):
        current_customer = self.find_customer(customer_id)
        for book in current_customer.loaned_books:
            if book_title.lower() == book.title.lower() and not book.is_available:
                book.is_available = True
                current_customer.loaned_books.remove(book)
                time = datetime.now().strftime("%d.%m.%Y %H:%M")
                for record in self.history.values():
                    if "return_time" not in record.keys() and record["book"] == book.book_id:
                        record["return_time"] = time
                        print(f"\"{book.title}\" returned to the library") 
                        self.continue_customer_session(customer_id) 
                        return
        print(f"Sorry,\"{book_title}\" is wrong book title")
        self.continue_customer_session(customer_id)

# takes the order from customer if a book is not in stock
# saves the order to history of orders
    def order_book(self, customer_id, new_book_title, new_book_author):
        current_customer = self.find_customer(customer_id)
        for book in self.books:
            if new_book_title.lower() == book.title.lower() and new_book_author.lower() == book.author.lower():
                print(f"We already have {book} in our library")
                self.continue_customer_session(customer_id)
                return
        time = datetime.now().strftime("%d.%m.%Y %H:%M")
        new_book_data = {"customer": customer_id, "new_book_title": new_book_title, "new_book_author": new_book_author, "order_time": time}
        all_orders_id = [order_id.split("_") for order_id in self.orders.keys()]
        new_order_number = (max((int(order_number[1]) for order_number in all_orders_id if order_number[0] == customer_id), default=0)) + 1
        new_order_id = f"{customer_id}_{new_order_number}"
        self.orders.update({new_order_id: new_book_data})
        self.save_orders(orders_file="orders.json")
        current_customer.orders.append({"new_book_title": new_book_title, "new_book_author": new_book_author, "order_time": time})
        print(f"\"{new_book_title}\" has been ordered. We'll try to add it to our library soon")
        self.continue_customer_session(customer_id)

# gives user oportunity to end his session in every moment
    def user_input(self, message):
        user_answer = input(message)
        exit_words = ["exit", "quit", "q", "x"]
        if user_answer.lower() in exit_words:
            print("Session ended. See you next time")
            self.new_customer_session()
        return user_answer

# starts a new customer session if customer already exist
# gives user oportunity to register as a customer
# saves all information if user quit the program
# reminds customer id if customer chooses "forgot"
    def new_customer_session(self):
        customer_id = input("\nEnter your customer id number (Type \"F\" if you forgot your customer id): ")
        if customer_id.lower() in ["exit", "quit", "q", "x"]:
             self.save_all_data()
             exit()
        elif customer_id.lower() in ["f", "forgot"]:
            self.add_customer_from_keyboard("forgot_id")
            self.new_customer_session()
        elif self.find_customer(customer_id):
            print(f"Hello {self.find_customer(customer_id)}! Welcome to the library \"{self.name}\"?")
            self.display_customer_action(customer_id)
        else:
            print("Customer not found")
            print(f"Do you want to register at the library \"{self.name}\"?")
            user_answer = self.user_input("Type \"Y\" for register, \"N\" for exit: ")
            if user_answer.lower() in ["y", "yes"]:
                self.add_customer_from_keyboard("registration")
                self.new_customer_session()
            elif user_answer.lower() in ["n", "no"]:
                print("Session ended")                
            else:
                print("Unacceptable answer. Session ended")
            self.new_customer_session()

# invites the customer to continue working with the program
    def continue_customer_session(self, customer_id):
        print("Do you want to continue?")
        user_answer = self.user_input("Type \"Y\" for continue, \"N\" for end session: ")
        if user_answer in ["y", "yes"]:
            self.display_customer_action(customer_id)
        elif user_answer in ["n", "no"]:
            print("Session ended. See you next time")
            self.new_customer_session()
        else:
            print("Unacceptable answer. Session ended")
            self.new_customer_session()

# invites the customer to select an action
# checks if this action is allowed to the customer
# displays actions and their resuls
# if customer choose action "borrow a book", displays most popular book
# if customer choose action "info", displays his borrowed and ordered books
    def display_customer_action(self, customer_id):
        current_customer = self.find_customer(customer_id)
        print("Please, select an action")
        action = self.user_input("Type \"B\" for borrow a book, \"R\" for return and \"O\" for order.\nFor information about your borrowed and ordered books type \"I\":\n")
        if action.lower() in ["b", "borrow"]:
            if current_customer.restrictions()["loan"]:
                self.display_popular_books()
                print("What book do you want to borrow?")
                book_title = self.user_input("Please, enter a title: ")
                self.loan_book(customer_id, book_title)
            else:
                print("You cannot take more than 2 books.\nTo borrow a new book you need to return some book")
        
        elif action.lower() in ["r", "return"]:
            if current_customer.restrictions()["return"]:
                print("What book do you want to return?")
                book_title = self.user_input("Please, enter a title: ")
                self.return_book(customer_id, book_title)
            else:
                print("You have no books for return")

        elif action.lower() in ["o", "order"]:
            if current_customer.restrictions()["order"]:
                print("What book do you want to order?")
                new_book_title = self.user_input("Please, enter a title: ")
                new_book_author = self.user_input("Please, enter an author: ")
                self.order_book(customer_id, new_book_title, new_book_author)
            else:
                print("You cannot order more than 2 books")

        elif action.lower() in ["i", "info", "information"]:
            if len(current_customer.loaned_books) == 0:
                print("You don't have any borrowed books now")
            else:
                print(f"You have {len(current_customer.loaned_books)} borrowed book(s) now:")
                current_customer.display_loaned_books(self)
            if len(current_customer.orders) == 0:
                print("You don't have any ordered books now")
            else:
                print(f"You have {len(current_customer.orders)} ordered book(s) now:")
                current_customer.display_orders(self)
        else:
            print("Unacceptable action")
        self.continue_customer_session(customer_id)

# runs the program
    def run(self):
        self.load_all_data()
        while True:
            try:
                self.new_customer_session()
            except KeyboardInterrupt:
                self.save_all_data()
                exit()

my_library = Library("BestBooks", "Haifa")
my_library.run()
