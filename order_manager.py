from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
import time
import datetime
from datetime import datetime, timedelta
import pyautogui
import CONSTS
import os
import tkinter as tk
import pygame

driver_path = "C:\\Program Files\\chromedriver.exe"
service = Service(driver_path)
browser = webdriver.Chrome(service=service)


def navigate_to_login_page(login_page_url):
    browser.get(login_page_url)


def login(username, password):
    wait = WebDriverWait(browser, 20)
    username_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[formcontrolname="login"]')))
    password_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[formcontrolname="password"]')))

    username_input.send_keys(username)
    password_input.send_keys(password)

    print("logging in..")
    submit_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.btn-submit')))
    submit_button.click()


def navigate_to_orders_page(page_url):
    print("navigating to orders page..")
    wait = WebDriverWait(browser, 20)
    wait.until(EC.url_contains(page_url))


def click_first_live_order_without_mock():
    wait = WebDriverWait(browser, 8)

    last_printed = datetime.now() - timedelta(minutes=1)

    while True:  # TODO: change this to depand on the trip timing
        try:
            row_locator = (By.XPATH, '//*[@id="statusReceived"]/div/div[2]')
            row_element = wait.until(EC.element_to_be_clickable(row_locator))
            row_element.click()
            timestamp = datetime.now().strftime("%H:%M")
            print(f"{timestamp}\tNew orders found. Extracting data...")
            break
        except TimeoutException:
            current_time = datetime.now()
            if current_time - last_printed >= timedelta(minutes=5):
                timestamp = current_time.strftime("%H:%M")
                print(f"{timestamp}\tNo live orders found. Waiting for new orders...")
                last_printed = current_time
            time.sleep(1)


def click_first_live_order(mock=False):
    # TODO: determine order viability before clicking (for packages)
    wait = WebDriverWait(browser, 8)

    last_printed = datetime.now() - timedelta(minutes=1)

    if not mock:
        while True:
            try:
                row_locator = (By.XPATH, '//*[@id="statusReceived"]/div/div[2]')
                row_element = wait.until(EC.element_to_be_clickable(row_locator))
                row_element.click()
                timestamp = datetime.now().strftime("%H:%M")
                print(f"{timestamp}\tNew orders found. Extracting data...")
                break
            except TimeoutException:
                current_time = datetime.now()
                if current_time - last_printed >= timedelta(minutes=5):
                    timestamp = current_time.strftime("%H:%M")
                    print(f"{timestamp}\tNo live orders found. Waiting for new orders...")
                    last_printed = current_time
                time.sleep(1)
    else:
        # Get the absolute path of the mock HTML file
        # mock_file_path = os.path.abspath("single_order_asap_mock.html")
        # mock_file_path = os.path.abspath("single_order_requesting_mock.html")
        # mock_file_path = os.path.abspath("single_order_multiple_mock.html")
        # mock_file_path = os.path.abspath("single_order_big_mock.html")
        mock_file_path = os.path.abspath("multiple_order_pultipreks_mock.html")

        # Use file:// protocol to load the local HTML file
        browser.get(f"file:///{mock_file_path}")


def add_country_code(number, country_code="+972"):
    if number.startswith(country_code) or number.startswith('+'):
        return number
    if number.startswith('0'):
        number = number[1:]
    number_with_country_code = country_code + number
    return number_with_country_code


def extract_order_info(order_info_element):
    order_extra_meals_locator = (By.CSS_SELECTOR, '.order_extra_meals')
    count_locator = (By.CSS_SELECTOR, 'span')
    extra_meal_locator = (By.CSS_SELECTOR, '.extra_meal')
    extra_meal_perks_locator = (By.CSS_SELECTOR, '.extra_meal_perks')

    order_extra_meals_elements = order_info_element.find_elements(*order_extra_meals_locator)

    extracted_data = []

    for order_extra_meals_element in order_extra_meals_elements:
        count_element = order_extra_meals_element.find_elements(*count_locator)
        count = int(count_element[0].text[1:]) if count_element else 1

        extra_meal_element = order_extra_meals_element.find_element(*extra_meal_locator)
        extra_meal = extra_meal_element.get_attribute('textContent').strip()

        extra_meal_perks_elements = order_extra_meals_element.find_elements(*extra_meal_perks_locator)
        extra_meal_perks = [perk.text.strip() for perk in extra_meal_perks_elements]

        for perk in extra_meal_perks:
            extra_meal = extra_meal.replace(perk, '').strip()

        extracted_data.append({
            'count': count,
            'dish': extra_meal,
            'sides': extra_meal_perks
        })

    return extracted_data


def extract_package_data_old():
    wait = WebDriverWait(browser, 10)
    package = []
    time.sleep(2)
    single_customer_locator = (By.CSS_SELECTOR, '.single_customer')
    company_name_locator = (By.CSS_SELECTOR, '.order_company')
    customer_address_locator = (By.CSS_SELECTOR, '.order_address')

    # Locate all .single_customer elements
    single_customer_elements = wait.until(EC.presence_of_all_elements_located(single_customer_locator))

    for single_customer_element in single_customer_elements:
        order_data = {}
        order_data.update(CONSTS.ORDER_STRUCTURE)

        # Update the locators to be relative to the single_customer_element
        customer_phone_locator = (By.CSS_SELECTOR, '.customer_phone')
        order_id_locator = (By.CSS_SELECTOR, '.customer_id')
        customer_name_locator = (By.CSS_SELECTOR, '.customer_name')
        order_time_locator = (By.CSS_SELECTOR, '.customer_time')
        order_amount_locator = (By.XPATH, './/div[contains(@class, "customer_time") and not(contains(@class, "forPrint2"))]')

        try:
            # company_name
            company_name_element = wait.until(EC.presence_of_element_located(company_name_locator))
            order_data['company_name'] = company_name_element.find_element(By.TAG_NAME, "strong").text

            # customer_address
            customer_address_element = wait.until(EC.presence_of_element_located(customer_address_locator))
            order_data['customer_address'] = customer_address_element.find_element(By.TAG_NAME, "strong").text

            # customer_phone TODO: fix  this. it is written Improperly
            customer_phone_element = single_customer_element.find_element(*customer_phone_locator)
            order_data['customer_phone'] = customer_phone_element.find_element(By.TAG_NAME, "strong").text
            order_data['customer_phone'] = add_country_code(order_data['customer_phone'])

            # order_id
            order_id_element = single_customer_element.find_element(*order_id_locator)
            order_data['order_id'] = order_id_element.find_element(By.TAG_NAME, "strong").text

            # customer_name
            customer_name_element = single_customer_element.find_element(*customer_name_locator)
            order_data['customer_name'] = customer_name_element.find_element(By.TAG_NAME, "strong").text

            # order_time
            order_time_element = single_customer_element.find_element(*order_time_locator)
            order_data['order_time'] = order_time_element.find_element(By.TAG_NAME, "strong").text

            # order_amount
            order_amount_element = single_customer_element.find_element(*order_amount_locator)
            order_data['order_amount'] = order_amount_element.find_element(By.TAG_NAME, "strong").text

            # order_info
            order_details_locator = (By.CSS_SELECTOR, '.order_details')
            order_details_element = single_customer_element.find_element(*order_details_locator)
            order_info_element = order_details_element.find_element(By.CSS_SELECTOR, ".order_info")

            # Extract the additional details
            try:
                additional_details_element = order_info_element.find_element(By.CSS_SELECTOR, ".dishes strong .a1")
                additional_details_text = additional_details_element.text
            except NoSuchElementException:
                additional_details_text = ""

            # Check for ASAP request
            asap_text = CONSTS.CIBUS_ASAP_TEXT
            if asap_text in additional_details_text:
                order_data['order_asap'] = True
                additional_details_text = additional_details_text.replace(asap_text, "").strip()

            # Check for special requests and store them in 'customer_note'
            if additional_details_text:
                order_data['customer_note'] = additional_details_text

            # Extract the extra meal text and organize it
            order_data['order_content'] = extract_order_info(order_info_element)

            # timestamp
            order_data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        except NoSuchElementException as e:
            print("Could not find an element for the current order:", e)
            print("Page source:")
            print(browser.page_source)

        package.append(order_data)

    return package


def extract_package_data():
    wait = WebDriverWait(browser, 10)
    package = []
    time.sleep(2)

    # Locate package attributes
    company_name_locator = (By.CSS_SELECTOR, '.order_company')
    customer_address_locator = (By.CSS_SELECTOR, '.order_address')

    # Locate all single customer elements in the package
    single_customer_locator = (By.CSS_SELECTOR, '.single_customer')
    single_customer_elements = wait.until(EC.presence_of_all_elements_located(single_customer_locator))

    for single_customer_element in single_customer_elements:
        order_data = {}
        order_data.update(CONSTS.ORDER_STRUCTURE)

        try:
            # company_name
            company_name_element = wait.until(EC.presence_of_element_located(company_name_locator))
            order_data['company_name'] = company_name_element.find_element(By.TAG_NAME, "strong").text

            # customer_address
            customer_address_element = wait.until(EC.presence_of_element_located(customer_address_locator))
            order_data['customer_address'] = customer_address_element.find_element(By.TAG_NAME, "strong").text

            # customer_phone
            customer_phone_locator = (By.CSS_SELECTOR, '.customer_phone')
            customer_phone_element = single_customer_element.find_element(*customer_phone_locator)
            phone_number = customer_phone_element.find_element(By.TAG_NAME, "strong").text
            order_data['customer_phone'] = add_country_code(phone_number)

            # order_id
            order_id_locator = (By.CSS_SELECTOR, '.customer_id')
            order_id_element = single_customer_element.find_element(*order_id_locator)
            order_data['order_id'] = order_id_element.find_element(By.TAG_NAME, "strong").text

            # customer_name
            customer_name_locator = (By.CSS_SELECTOR, '.customer_name')
            customer_name_element = single_customer_element.find_element(*customer_name_locator)
            order_data['customer_name'] = customer_name_element.find_element(By.TAG_NAME, "strong").text

            # order_time
            order_time_locator = (By.CSS_SELECTOR, '.customer_time')
            order_time_element = single_customer_element.find_element(*order_time_locator)
            order_data['order_time'] = order_time_element.find_element(By.TAG_NAME, "strong").text

            # order_amount
            amount_xpath = './/div[contains(@class, "customer_time") and not(contains(@class, "forPrint2"))]'
            order_amount_locator = (By.XPATH, amount_xpath)
            order_amount_element = single_customer_element.find_element(*order_amount_locator)
            order_data['order_amount'] = order_amount_element.find_element(By.TAG_NAME, "strong").text

            # order_info
            order_details_locator = (By.CSS_SELECTOR, '.order_details')
            order_details_element = single_customer_element.find_element(*order_details_locator)
            order_info_element = order_details_element.find_element(By.CSS_SELECTOR, ".order_info")

            # Extract additional details
            try:
                additional_details_element = order_info_element.find_element(By.CSS_SELECTOR, ".dishes strong .a1")
                additional_details_text = additional_details_element.text
            except NoSuchElementException:
                additional_details_text = ""

            # order_asap
            asap_text = CONSTS.CIBUS_ASAP_TEXT
            if asap_text in additional_details_text:
                order_data['order_asap'] = True
                additional_details_text = additional_details_text.replace(asap_text, "").strip()

            # customer_note
            if additional_details_text:
                order_data['customer_note'] = additional_details_text

            # order_content
            order_data['order_content'] = extract_order_info(order_info_element)

            # status
            order_data['status'] = CONSTS.ACCEPTED

            # timestamp
            order_data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        except NoSuchElementException as e:
            print("Could not find an element for the current order:", e)
            print("Page source:")
            print(browser.page_source)

        package.append(order_data)

    return package


def extract_package_data_subbed():

    def _extract_customer_info(single_customer_element):
        # Extracts customer information from a .single_customer element
        # Returns a dictionary with the customer information

        # Update the locators to be relative to the single_customer_element
        company_name_locator = (By.CSS_SELECTOR, '.order_company')
        customer_address_locator = (By.CSS_SELECTOR, '.order_address')
        customer_phone_locator = (By.CSS_SELECTOR, '.customer_phone')
        order_id_locator = (By.CSS_SELECTOR, '.customer_id')
        customer_name_locator = (By.CSS_SELECTOR, '.customer_name')
        order_time_locator = (By.CSS_SELECTOR, '.customer_time')
        order_amount_locator = (
        By.XPATH, './/div[contains(@class, "customer_time") and not(contains(@class, "forPrint2"))]')

        try:
            # company_name
            company_name_element = wait.until(EC.presence_of_element_located(company_name_locator))
            company_name = company_name_element.find_element(By.TAG_NAME, "strong").text

            # customer_address
            customer_address_element = wait.until(EC.presence_of_element_located(customer_address_locator))
            customer_address = customer_address_element.find_element(By.TAG_NAME, "strong").text

            # customer_phone
            customer_phone_element = single_customer_element.find_element(*customer_phone_locator)
            customer_phone_plain = customer_phone_element.find_element(By.TAG_NAME, "strong").text
            customer_phone = add_country_code(customer_phone_plain)

            # order_id
            order_id_element = single_customer_element.find_element(*order_id_locator)
            order_id = order_id_element.find_element(By.TAG_NAME, "strong").text

            # customer_name
            customer_name_element = single_customer_element.find_element(*customer_name_locator)
            customer_name = customer_name_element.find_element(By.TAG_NAME, "strong").text

            # order_time
            order_time_element = single_customer_element.find_element(*order_time_locator)
            order_time = order_time_element.find_element(By.TAG_NAME, "strong").text

            # order_amount
            order_amount_element = single_customer_element.find_element(*order_amount_locator)
            order_amount = order_amount_element.find_element(By.TAG_NAME, "strong").text

            # Additional details - order_asap and customer_note
            try:
                additional_details_element = single_customer_element.find_element(By.CSS_SELECTOR, ".dishes strong .a1")
                additional_details_text = additional_details_element.text
            except NoSuchElementException:
                additional_details_text = ""

            # order_asap
            if CONSTS.CIBUS_ASAP_TEXT in additional_details_text:
                order_asap = True
                additional_details_text = additional_details_text.replace(CONSTS.CIBUS_ASAP_TEXT, "").strip()
            else:
                order_asap = False

            # customer_note
            if additional_details_text:
                customer_note = additional_details_text
            else:
                customer_note = ""

            # timestamp
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')


        except NoSuchElementException as e:
            print("Could not find an element for the current order:", e)
            print("Page source:")
            print(browser.page_source)

        return {
            "company_name": company_name,
            "customer_address": customer_address,
            "customer_phone": customer_phone,
            "order_id": order_id,
            "customer_name": customer_name,
            "order_time": order_time,
            "order_amount": order_amount,
            "order_asap": order_asap,
            "customer_note": customer_note,
            "timestamp": timestamp
        }

    def _extract_extra_meals(single_customer_element):
        # Extracts the meals from a .single_customer element
        # Returns a list of meals

        # order_info
        order_details_locator = (By.CSS_SELECTOR, '.order_details')
        order_details_element = single_customer_element.find_element(*order_details_locator)
        order_info_element = order_details_element.find_element(By.CSS_SELECTOR, ".order_info")

        # Extract the extra meal text
        extra_meal_elements = order_info_element.find_elements(By.CSS_SELECTOR, ".order_extra_meals")
        extra_meal_texts = []

        for extra_meal_element in extra_meal_elements:
            extra_meal_text = extra_meal_element.text
            extra_meal_texts.append(extra_meal_text)

        meals = []

        main_dish_element = single_customer_element.find_element(By.CSS_SELECTOR, ".extra_meal")
        main_dish = _process_main_dish(main_dish_element)

        if main_dish:
            meals.append(main_dish)

        extra_meal_elements = single_customer_element.find_elements(By.CSS_SELECTOR, ".extra_meal_perks")
        for extra_meal_element in extra_meal_elements:
            split_text = extra_meal_element.text.split('|')

            dish_name = split_text[0].strip()

            for chef in CONSTS.CHEFS_NAMES:
                if chef in split_text[1]:
                    meals.append({"dish_name": dish_name, "chef_name": chef, "count": 1})
                    break

        return meals

    def _process_main_dish(main_dish_element):
        main_dish = {}
        split_text = main_dish_element.text.split('|')
        dish_name = split_text[0].strip()

        for chef in CONSTS.CHEFS_NAMES:
            if chef in split_text[1]:
                main_dish = {"dish_name": dish_name, "chef_name": chef, "count": 1}
                break

        return main_dish

    def _process_extra_meal_elements(extra_meal_elements):
        # Processes the extra_meal_elements and returns a list of dictionaries containing the extra meal data
        extra_meals = []

        for extra_meal_element in extra_meal_elements:
            count_span_elements = extra_meal_element.find_elements(By.TAG_NAME, 'span')
            count = int(count_span_elements[0].text[1:]) if count_span_elements else 1

            extra_meal = extra_meal_element.find_element(By.CSS_SELECTOR, ".extra_meal")
            split_text = extra_meal.text.split('|')

            dish_name = split_text[0].strip()

            for chef in CONSTS.CHEFS_NAMES:
                if chef in split_text[1]:
                    extra_meals.append({"dish_name": dish_name, "chef_name": chef, "count": count})
                    break

            perks = extra_meal_element.find_elements(By.CSS_SELECTOR, ".extra_meal_perks")
            for perk in perks:
                perk_text = perk.text
                for chef in CONSTS.CHEFS_NAMES:
                    if chef in perk_text:
                        split_perk_text = perk_text.split('|')
                        perk_dish_name = split_perk_text[0].strip()
                        extra_meals.append({"dish_name": perk_dish_name, "chef_name": chef, "count": count})
                        break

        return extra_meals

    wait = WebDriverWait(browser, 10)
    package = []
    time.sleep(2)

    # Locate all .single_customer elements
    single_customer_locator = (By.CSS_SELECTOR, '.single_customer')
    single_customer_elements = wait.until(EC.presence_of_all_elements_located(single_customer_locator))

    # Use helper functions:

    for single_customer_element in single_customer_elements:
        order_data = {}
        order_data.update(CONSTS.ORDER_STRUCTURE)

        customer_info = _extract_customer_info(single_customer_element)
        order_data.update(customer_info)

        extra_meals = _extract_extra_meals(single_customer_element)
        order_data["order_content"] = extra_meals
        package.append(order_data)

    return package


def print_to_screen(orders_list):
    for order_data in orders_list:
        for key, value in order_data.items():
            print(f"{key}: {value}")


def print_package():

    # TEST
    # print("printing via the function 'print_package()' is passed due to test mode")
    # return

    # TODO make the printing work even if i am not currently on the page
    wait = WebDriverWait(browser, 10)

    # Define the locator for the print button
    print_button_locator = (By.CSS_SELECTOR, '.to_print.button.is_save')

    # Wait for the button to be clickable
    print_button = wait.until(EC.element_to_be_clickable(print_button_locator))

    # Use JavaScript to click the button even if the window is not in focus
    browser.execute_script("arguments[0].click();", print_button)

    # Wait for the print dialog to appear
    time.sleep(2)

    # Press the Enter key to click the Print button in the dialog
    pyautogui.press('enter')


def reject_order():
    # TODO
    #  extract package data into database and determine status
    #  update order status
    return


def ask_human(order_amount):
    # TODO test this after changes
    def _play_sound(filename):
        pygame.mixer.init()
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

    def _on_accept():
        window.result = CONSTS.ACCEPTED
        window.destroy()

    def _on_reject():
        window.result = CONSTS.REJECTED
        window.destroy()

    _play_sound(CONSTS.MINIMUM_SOUND_ALERT)

    window = tk.Tk()
    window.title("Order Review")

    # order_info = f"Order ID: {order_data['order_id']}\n"
    # order_info += f"Company Name: {order_data['company_name']}\n"
    # order_info += f"Order Amount: {order_data['order_amount']}\n"
    # order_info += f"Customer Name: {order_data['customer_name']}\n"
    # order_info += f"Customer Address: {order_data['customer_address']}\n"

    order_info = f"Order amount: {order_amount}\n"

    label = tk.Label(window, text=order_info, padx=20, pady=20)
    label.pack()

    accept_button = tk.Button(window, text="Accept Order", command=_on_accept)
    accept_button.pack(padx=10, pady=10)

    reject_button = tk.Button(window, text="Reject Order", command=_on_reject)
    reject_button.pack(padx=10, pady=10)

    window.result = CONSTS.WAITING
    window.mainloop()

    return window.result


def determine_order_status_and_update(order_data):
    order_amount_str = order_data.get('order_amount', '0').split(' ')[0]
    if float(order_amount_str) < CONSTS.MINIMUM_ORDER_AMOUNT:
        order_status = ask_human(order_data)
    else:
        order_status = CONSTS.ACCEPTED

    # Update the order status and call back_home function
    order_data['status'] = order_status
    back_home(order_data['status'])

    return order_status


def back_home(status):
    if status == CONSTS.ACCEPTED:
        print_package()
    elif status == CONSTS.REJECTED:
        # TODO: change this part as with the new structure these elif, else, are probably redundant
        reject_order()
        print("order rejected and did not sent to print.")
    else:
        print("Error. Invalid order status.Order did not sent to print.")

    wait = WebDriverWait(browser, 10)

    # Define the locator for the "back_home" button
    back_home_locator = (By.CSS_SELECTOR, '.back_home')

    # Wait for the button to be clickable and click it
    back_home_button = wait.until(EC.element_to_be_clickable(back_home_locator))
    back_home_button.click()
    time.sleep(2)


def set_package_status():
    order_amount_locator = (By.CSS_SELECTOR, ".order_holder .order_price span")

    try:
        # Locate the order amount element
        wait = WebDriverWait(browser, 10)
        order_amount_element = wait.until(EC.presence_of_element_located(order_amount_locator))

        # Extract the order amount
        order_amount_str = order_amount_element.text.replace('\u200F', '').replace('₪', '').strip()
        order_amount = float(order_amount_str)

        # Set the package status based on the order amount
        if order_amount < CONSTS.MINIMUM_ORDER_AMOUNT:
            status = ask_human(order_amount)  # Assuming you have a function called 'ask_human()' to handle this case
        else:
            status = CONSTS.ACCEPTED

    except Exception as e:
        print("Could not find the order amount:", e)
        status = CONSTS.ACCEPTED  # Assuming you want to default to ACCEPTED status if there's an error

    return status


def process_package():
    if set_package_status() == CONSTS.ACCEPTED:
        click_first_live_order(mock=False)
        package = extract_package_data()
        print_to_screen(package)  # control function
        back_home(status=CONSTS.ACCEPTED)  # TODO: test this as I changed the order things happen in here
        return package

    else:
        reject_order()


def site_connection():
    login_page_url = 'https://cibusrest.mysodexo.co.il/login'
    navigate_to_login_page(login_page_url)

    username = "rest_142933_contact"  # Replace with your username
    password = "Maidiz@1993"  # Replace with your password
    login(username, password)

    orders_page_url = 'https://cibusrest.mysodexo.co.il/orders'
    navigate_to_orders_page(orders_page_url)


def close_connection():
    browser.quit()
