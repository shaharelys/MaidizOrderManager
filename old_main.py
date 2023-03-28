import multiprocessing
import time
from db_manager import update_db_function
from contacts_manager import save_contact_function


def run_update_db():
    while True:
        update_db_function()
        time.sleep(1)  # Add a small sleep to allow the other function to run


def run_save_contact():
    while True:
        save_contact_function()
        time.sleep(1)  # Add a small sleep to allow the other function to run


def main():
    p1 = multiprocessing.Process(target=run_update_db)
    p2 = multiprocessing.Process(target=run_save_contact)

    p1.start()
    p2.start()

    p1.join()
    p2.join()


if __name__ == '__main__':
    main()
