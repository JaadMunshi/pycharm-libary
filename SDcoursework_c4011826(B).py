import os
import sys

# Data storage
staff = []
books = []
borrowers = []
loans = []
current_user = None
login_attempts = {}


def load_data():

    global staff, books, borrowers, loans

    # Load staff data
    if os.path.exists("staff.csv"):
        with open("staff.csv") as f:
            headers = f.readline().strip().split(',')
            for line in f:
                values = line.strip().split(',')
                staff.append(dict(zip(headers, values)))

    # Load books data
    if os.path.exists("inventories.csv"):
        with open("inventories.csv") as f:
            headers = f.readline().strip().split(',')
            for line in f:
                values = line.strip().split(',')
                books.append(dict(zip(headers, values)))

    # Load borrowers data
    if os.path.exists("borrowers.csv"):
        with open("borrowers.csv") as f:
            headers = f.readline().strip().split(',')
            for line in f:
                values = line.strip().split(',')
                borrowers.append(dict(zip(headers, values)))

    # Load loans data
    if os.path.exists("loaned.csv"):
        with open("loaned.csv") as f:
            headers = f.readline().strip().split(',')
            for line in f:
                values = line.strip().split(',')
                loans.append(dict(zip(headers, values)))


def save_data():
    """Save data back to CSV files"""
    # Save staff
    with open("staff.csv", "w") as f:
        f.write("UserID,Name,Role,Email,PhoneNumber,HireDate,Password,Status\n")
        for person in staff:
            f.write(f"{person['UserID']},{person['Name']},{person['Role']},")
            f.write(f"{person['Email']},{person['PhoneNumber']},{person['HireDate']},")
            f.write(f"{person['Password']},{person['Status']}\n")

    # Save books
    with open("inventories.csv", "w") as f:
        f.write("BookID,Title,Author,Genre,PublishedYear,TotalCopies,CopiesAvailable,OnLoan,Deleted\n")
        for book in books:
            f.write(f"{book['BookID']},{book['Title']},{book['Author']},")
            f.write(f"{book['Genre']},{book['PublishedYear']},{book['TotalCopies']},")
            f.write(f"{book['CopiesAvailable']},{book['OnLoan']},{book['Deleted']}\n")

    # Save loans
    with open("loaned.csv", "w") as f:
        f.write("BookID,BorrowerID,Due\n")
        for loan in loans:
            f.write(f"{loan['BookID']},{loan['BorrowerID']},{loan['Due']}\n")


def clear_screen():
    """Clear the console screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def login():
    """Login with 3 attempt limit and account blocking"""
    global current_user, login_attempts

    clear_screen()
    print("=== Library Login ===")
    user_id = input("User ID: ")
    password = input("Password: ")

    # Find user
    user = None
    for person in staff:
        if person['UserID'] == user_id:
            user = person
            break

    if not user:
        print("Invalid user ID")
        input("Press Enter to continue...")
        return False

    # Check account status
    if user['Status'] != 'active':
        print(f"Account is {user['Status']}")
        input("Press Enter to continue...")
        return False

    # Check password
    if user['Password'] == password:
        current_user = user
        login_attempts[user_id] = 0  # Reset attempts
        return True
    else:
        # Track failed attempts
        if user_id in login_attempts:
            login_attempts[user_id] += 1
        else:
            login_attempts[user_id] = 1

        # Block after 3 attempts
        if login_attempts[user_id] >= 3:
            for person in staff:
                if person['UserID'] == user_id:
                    person['Status'] = 'blocked'
                    save_data()
                    print("Account blocked! Too many failed attempts.")
                    input("Press Enter to continue...")
                    return False

        print(f"Wrong password! Attempts left: {3 - login_attempts[user_id]}")
        input("Press Enter to continue...")
        return False


def librarian_menu():
    """Menu for librarians"""
    while True:
        clear_screen()
        print(f"=== Welcome {current_user['Name']} (Librarian) ===")
        print("1. Loan a book")
        print("2. Return a book")
        print("3. Extend loan")
        print("4. Search books")
        print("5. Logout")

        choice = input("Choose option: ")

        if choice == "1":
            # Loan book
            borrower_id = input("Borrower ID: ")
            book_id = input("Book ID: ")

            # Check borrower exists
            borrower_exists = False
            for b in borrowers:
                if b['BorrowerID'] == borrower_id:
                    borrower_exists = True
                    break

            if not borrower_exists:
                print("Borrower not found")
                input("Press Enter to continue...")
                continue

            # Find available book
            book = None
            for b in books:
                if b['BookID'] == book_id and b['Deleted'] == '0' and int(b['CopiesAvailable']) > 0:
                    book = b
                    break

            if book:
                # Calculate due date (14 days from today)
                due_date = input("Due date (DD/MM/YYYY): ")  # In real app, calculate this

                # Record loan
                loans.append({
                    'BookID': book_id,
                    'BorrowerID': borrower_id,
                    'Due': due_date
                })

                # Update book status
                book['CopiesAvailable'] = str(int(book['CopiesAvailable']) - 1)
                book['OnLoan'] = str(int(book['OnLoan']) + 1)
                save_data()
                print("Book loaned successfully!")
            else:
                print("Book not available")
            input("Press Enter to continue...")

        elif choice == "2":
            # Return book
            book_id = input("Book ID to return: ")

            # Find and remove loan
            loan_found = False
            for i, loan in enumerate(loans):
                if loan['BookID'] == book_id:
                    loans.pop(i)
                    loan_found = True

                    # Update book status
                    for book in books:
                        if book['BookID'] == book_id:
                            book['CopiesAvailable'] = str(int(book['CopiesAvailable']) + 1)
                            book['OnLoan'] = str(int(book['OnLoan']) - 1)
                            save_data()
                            print("Book returned successfully!")
                            break
                    break

            if not loan_found:
                print("No active loan found for this book")
            input("Press Enter to continue...")

        elif choice == "3":
            # Extend loan
            book_id = input("Book ID to extend: ")

            # Find loan
            loan_found = False
            for loan in loans:
                if loan['BookID'] == book_id:
                    # Calculate new due date (14 days from current due)
                    new_due = input("New due date (DD/MM/YYYY): ")  # In real app, calculate this
                    loan['Due'] = new_due
                    save_data()
                    print("Loan extended successfully!")
                    loan_found = True
                    break

            if not loan_found:
                print("No active loan found for this book")
            input("Press Enter to continue...")

        elif choice == "4":
            # Search books
            search_term = input("Enter book ID or title: ")
            found = False

            for book in books:
                if (search_term == book['BookID'] or
                    search_term.lower() in book['Title'].lower()) and book['Deleted'] == '0':
                    print(f"\nID: {book['BookID']}")
                    print(f"Title: {book['Title']}")
                    print(f"Author: {book['Author']}")
                    print(f"Available: {book['CopiesAvailable']}/{book['TotalCopies']}")
                    found = True

            if not found:
                print("No matching books found")
            input("Press Enter to continue...")

        elif choice == "5":
            break


def supervisor_menu():
    """Menu for supervisors"""
    while True:
        clear_screen()
        print(f"=== Welcome {current_user['Name']} (Supervisor) ===")
        print("1. Add new book")
        print("2. Update book status")
        print("3. Manage accounts")
        print("4. Logout")

        choice = input("Choose option: ")

        if choice == "1":
            # Add new book
            new_book = {
                'BookID': input("Book ID: "),
                'Title': input("Title: "),
                'Author': input("Author: "),
                'Genre': input("Genre: "),
                'PublishedYear': input("Year: "),
                'TotalCopies': input("Total copies: "),
                'CopiesAvailable': input("Total available copies: "),  # Same as total for new book
                'OnLoan': '0',
                'Deleted': '0'
            }
            books.append(new_book)
            save_data()
            print("Book added successfully!")
            input("Press Enter to continue...")

        elif choice == "2":
            # Update book status
            book_id = input("Book ID: ")
            book_found = False

            for book in books:
                if book['BookID'] == book_id:
                    book_found = True
                    print("\nCurrent status:")
                    print(f"Available: {book['CopiesAvailable']}")
                    print(f"On Loan: {book['OnLoan']}")
                    print(f"Deleted: {'Yes' if book['Deleted'] == '1' else 'No'}")

                    print("\nSet new status:")
                    print("1. Available")
                    print("2. On Loan")
                    print("3. Deleted")

                    status_choice = input("Your choice: ")

                    if status_choice == "1":
                        book['CopiesAvailable'] = book['TotalCopies']
                        book['OnLoan'] = '0'
                        book['Deleted'] = '0'
                    elif status_choice == "2":
                        book['CopiesAvailable'] = '0'
                        book['OnLoan'] = book['TotalCopies']
                        book['Deleted'] = '0'
                    elif status_choice == "3":
                        book['Deleted'] = '1'

                    save_data()
                    print("Status updated!")
                    break

            if not book_found:
                print("Book not found")
            input("Press Enter to continue...")

        elif choice == "3":
            # Manage accounts
            print("\nStaff Accounts:")
            for person in staff:
                print(f"{person['UserID']}: {person['Name']} ({person['Status']})")

            user_id = input("\nEnter user ID to update: ")
            user_found = False

            for person in staff:
                if person['UserID'] == user_id:
                    user_found = True
                    print("\nCurrent status:", person['Status'])
                    print("Set new status:")
                    print("1. active")
                    print("2. blocked")
                    print("3. inactive")

                    status_choice = input("Your choice: ")

                    if status_choice == "1":
                        person['Status'] = 'active'
                    elif status_choice == "2":
                        person['Status'] = 'blocked'
                    elif status_choice == "3":
                        person['Status'] = 'inactive'

                    save_data()
                    print("Status updated!")
                    break

            if not user_found:
                print("User not found")
            input("Press Enter to continue...")

        elif choice == "4":
            break


def main():
    """Main program"""
    load_data()

    while True:
        clear_screen()
        print("=== Library Management System ===")
        print("1. Login")
        print("2. Exit")

        choice = input("Choose option: ")

        if choice == "1":
            if login():
                if current_user['Role'] == 'Librarian':
                    librarian_menu()
                else:
                    supervisor_menu()
        elif choice == "2":
            print("Goodbye!")
            break


if __name__ == "__main__":
    main()