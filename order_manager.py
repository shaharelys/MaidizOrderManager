from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
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
import pygetwindow as gw
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
    if CONSTS.MOCK:
        # mock_file_path = os.path.abspath("mock pages/single_order_big_mock.html")
        mock_file_path = os.path.abspath("mock pages/orders_below_min_order.html")

        # Use file:// protocol to load the local HTML file
        browser.get(f"file:///{mock_file_path}")
    else:
        wait.until(EC.url_contains(page_url))


def click_first_live_order():
    wait = WebDriverWait(browser, 8)

    last_printed = datetime.now() - timedelta(minutes=1)

    if not CONSTS.MOCK:
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
                    print(f"click_first_live_order | {timestamp}\tNo live orders found. Waiting for new orders...")
                    last_printed = current_time
                time.sleep(1)
    else:
        # Get the absolute path of the mock HTML file
        # mock_file_path = os.path.abspath("mock pages/single_order_asap_mock.html")
        # mock_file_path = os.path.abspath("mock pages/single_order_requesting_mock.html")
        # mock_file_path = os.path.abspath("mock pages/single_order_multiple_mock.html")
        # mock_file_path = os.path.abspath("mock pages/single_order_big_mock.html")
        # mock_file_path = os.path.abspath("mock pages/multiple_order_pultipreks_mock.html")
        mock_file_path = os.path.abspath("mock pages/order_to_add_to db_mock.html")

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
            # customer_company
            company_name_element = wait.until(EC.presence_of_element_located(company_name_locator))
            order_data['customer_company'] = company_name_element.find_element(By.TAG_NAME, "strong").text

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
            order_data['order_id'] = int(order_id_element.find_element(By.TAG_NAME, "strong").text)

            # customer_name
            customer_name_locator = (By.CSS_SELECTOR, '.customer_name')
            customer_name_element = single_customer_element.find_element(*customer_name_locator)
            order_data['customer_name'] = customer_name_element.find_element(By.TAG_NAME, "strong").text

            # order_expected
            order_time_locator = (By.CSS_SELECTOR, '.customer_time')
            order_time_element = single_customer_element.find_element(*order_time_locator)
            order_data['order_expected'] = order_time_element.find_element(By.TAG_NAME, "strong").text

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
            order_data['order_status'] = CONSTS.ACCEPTED

            # timestamp
            order_data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        except NoSuchElementException as e:
            print("Could not find an element for the current order:", e)
            print("Page source:")
            print(browser.page_source)

        package.append(order_data)

    return package


def print_to_screen(orders_list):
    for order_data in orders_list:
        print("*"*60)
        for key, value in order_data.items():
            print(f"{key}: {value}")


def print_package_old():
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


def print_package():
    wait = WebDriverWait(browser, 20)

    # Define the locator for the print button
    print_button_locator = (By.CSS_SELECTOR, '.to_print.button.is_save')

    # Wait for the button to be clickable
    print_button = wait.until(EC.element_to_be_clickable(print_button_locator))

    # Bring the browser window to focus
    browser_title = browser.title
    browser_window = gw.getWindowsWithTitle(browser_title)[0]
    try:
        browser_window.activate()
    except gw.PyGetWindowException:
        print("Warning: Could not bring the browser window to focus.")

    # Use JavaScript to click the button
    browser.execute_script("arguments[0].click();", print_button)

    # Wait for the print dialog to appear
    time.sleep(10)

    # Press the Enter key to click the Print button in the dialog
    pyautogui.press('enter')


def reject_order():
    # TODO
    #  extract package data into database and determine status
    #  update order status
    return


def ask_human(total):
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
    window.lift()

    # order_info = f"Order ID: {order_data['order_id']}\n"
    # order_info += f"Company Name: {order_data['customer_company']}\n"
    # order_info += f"Order Amount: {order_data['order_amount']}\n"
    # order_info += f"Customer Name: {order_data['customer_name']}\n"
    # order_info += f"Customer Address: {order_data['customer_address']}\n"

    order_info = f"Order amount: {total}\n"
    order_info += f"\n" \
                  f"יניב יניב יקר\nניתן לדחות הזמנות רק דרך אתר סיבוס" \
                  f"\n" \
                  f"בברכה" \
                  f"\n" \
                  f"יניב יניב"

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


def back_home_old(status=CONSTS.ACCEPTED):
    if status == CONSTS.ACCEPTED:
        print_package()

    wait = WebDriverWait(browser, 10)

    # Define the locator for the "back_home" button
    back_home_locator = (By.CSS_SELECTOR, '.back_home')

    # Wait for the button to be clickable and click it
    back_home_button = wait.until(EC.element_to_be_clickable(back_home_locator))
    back_home_button.click()
    time.sleep(2)


def back_home():
    wait = WebDriverWait(browser, 10)

    # Define the locator for the "back_home" button
    back_home_locator = (By.CSS_SELECTOR, '.back_home')

    # Wait for the button to be clickable and click it
    back_home_button = wait.until(EC.element_to_be_clickable(back_home_locator))
    back_home_button.click()
    time.sleep(2)


def set_package_status():
    order_amount_locator = (By.CSS_SELECTOR, ".order_holder .order_price span")
    row_locator = (By.XPATH, '//*[@id="statusReceived"]/div/div[2]')
    last_printed = datetime.now() - timedelta(minutes=5)

    while True:
        try:
            wait = WebDriverWait(browser, 10)
            # Check if there are incoming orders
            row_elements = wait.until(EC.presence_of_all_elements_located(row_locator))
            if len(row_elements) == 0:
                print("No incoming orders.")
                time.sleep(1)
                continue

            # Locate the order amount element
            order_amount_element = wait.until(EC.presence_of_element_located(order_amount_locator))

            # Extract the order amount
            order_amount_str = order_amount_element.text.replace('\u200F', '').replace('₪', '').strip()
            order_amount = float(order_amount_str)

            # Set the package status based on the order amount
            if order_amount < CONSTS.MINIMUM_ORDER_AMOUNT:
                status = ask_human(order_amount)  # Assuming you have a function called 'ask_human()' to handle this case
            else:
                status = CONSTS.ACCEPTED
            break

        except TimeoutException:
            current_time = datetime.now()
            if current_time - last_printed >= timedelta(minutes=5):
                timestamp = current_time.strftime("%H:%M")
                print(f"set_package_status | {timestamp}\tNo live orders found. Waiting for new orders...")
                last_printed = current_time
            time.sleep(1)

        except Exception as e:
            print("Could not find the order amount:", e)
            status = CONSTS.ACCEPTED
            break

    return status


def process_package_old():
    mock = CONSTS.MOCK
    status = set_package_status()
    if status == CONSTS.ACCEPTED:
        click_first_live_order()
        package = extract_package_data()
        # TODO: move the below to main, and print only after adding to db and sending Whatsapp
        print_to_screen(package)  # control function
        back_home(status)  # TODO: test this as I changed the order things happen in here
        return package

    else:
        reject_order()


def process_package():
    click_first_live_order()
    package = extract_package_data()
    return package


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
