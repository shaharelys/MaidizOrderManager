import multiprocessing
from db_manager import update_db_function
from contacts_manager import save_contact_function

def run_update_db(lock):
    while True:
        update_db_function(lock)

def run_save_contact(lock):
    while True:
        save_contact_function(lock)

if __name__ == "__main__":
    lock = multiprocessing.Lock()
    process1 = multiprocessing.Process(target=run_update_db, args=(lock,))
    process2 = multiprocessing.Process(target=run_save_contact, args=(lock,))

    process1.start()
    process2.start()

    process1.join()
    process2.join()
