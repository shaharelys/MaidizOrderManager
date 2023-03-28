
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
from datetime import datetime, timedelta
import pyautogui
from playsound import playsound

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


def click_first_live_order():
    wait = WebDriverWait(browser, 8)

    last_printed = datetime.now() - timedelta(minutes=1)

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
            if current_time - last_printed >= timedelta(minutes=1):
                timestamp = current_time.strftime("%H:%M")
                print(f"{timestamp}\tNo live orders found. Waiting for new orders...")
                last_printed = current_time
            time.sleep(1)


def extract_order_data():
    wait = WebDriverWait(browser, 10)
    order_data = {}
    time.sleep(2)
    company_name_locator = (By.CSS_SELECTOR, '.order_company')
    company_phone_locator = (By.CSS_SELECTOR, '.order_phone')
    customer_address_locator = (By.CSS_SELECTOR, '.order_address')
    customer_phone_locator = (By.CSS_SELECTOR, '.customer_phone')
    order_id_locator = (By.CSS_SELECTOR, '.customer_id')
    customer_name_locator = (By.CSS_SELECTOR, '.customer_name')
    order_time_locator = (By.CSS_SELECTOR, '.customer_time')
    order_amount_locator = (By.XPATH, '//div[contains(@class, "customer_time") and not(contains(@class, "forPrint2"))]')

    try:
        # company_name
        company_name_element = wait.until(EC.presence_of_element_located(company_name_locator))
        order_data['company_name'] = company_name_element.find_element(By.TAG_NAME, "strong").text

        # company_phone
        company_phone_element = wait.until(EC.presence_of_element_located(company_phone_locator))
        order_data['company_phone'] = company_phone_element.find_element(By.TAG_NAME, "strong").text

        # customer_address
        customer_address_element = wait.until(EC.presence_of_element_located(customer_address_locator))
        order_data['customer_address'] = customer_address_element.find_element(By.TAG_NAME, "strong").text

        # customer_phone
        customer_phone_element = wait.until(EC.presence_of_element_located(customer_phone_locator))
        order_data['customer_phone'] = customer_phone_element.find_element(By.TAG_NAME, "strong").text

        # order_id
        order_id_element = wait.until(EC.presence_of_element_located(order_id_locator))
        order_data['order_id'] = order_id_element.find_element(By.TAG_NAME, "strong").text

        # customer_name
        customer_name_element = wait.until(EC.presence_of_element_located(customer_name_locator))
        order_data['customer_name'] = customer_name_element.find_element(By.TAG_NAME, "strong").text

        # order_time
        order_time_element = wait.until(EC.presence_of_element_located(order_time_locator))
        order_data['order_time'] = order_time_element.find_element(By.TAG_NAME, "strong").text

        # order_amount
        order_amount_element = wait.until(EC.presence_of_element_located(order_amount_locator))
        order_data['order_amount'] = order_amount_element.find_element(By.TAG_NAME, "strong").text


    except TimeoutError:
        print("Could not find the element for company_name.")
        order_data['company_name'] = None

    return order_data


def print_to_screen(order_data):
    for key, value in order_data.items():
        print(f"{key}: {value}")


def print_package_old():

    # TEST
    # print("printing via the function 'print_package()' is passed due to test mode")
    # return

    # TODO make the printing work even if i am not currently on the page
    wait = WebDriverWait(browser, 10)

    # Define the locator for the print button
    print_button_locator = (By.CSS_SELECTOR, '.to_print.button.is_save')

    # Wait for the button to be clickable
    print_button = wait.until(EC.element_to_be_clickable(print_button_locator))

    # Click the button
    print_button.click()

    # Wait for the print dialog to appear
    time.sleep(2)

    # Press the Enter key to click the Print button in the dialog
    pyautogui.press('enter')


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


def back_home():
    wait = WebDriverWait(browser, 10)

    # Define the locator for the "back_home" button
    back_home_locator = (By.CSS_SELECTOR, '.back_home')

    # Wait for the button to be clickable and click it
    back_home_button = wait.until(EC.element_to_be_clickable(back_home_locator))
    back_home_button.click()
    time.sleep(2)


def process_order_old():
    click_first_live_order()
    order_data = extract_order_data()
    print_to_screen(order_data)  # control function
    print_package()
    time.sleep(3)
    back_home()
    return order_data


def play_sound(filename):
    playsound(filename)


def process_order():
    click_first_live_order()
    order_data = extract_order_data()
    print_to_screen(order_data)  # control function

    order_amount_str = order_data.get('order_amount', '0').split(' ')[0]
    extracted_order_amount = float(order_amount_str)
    if extracted_order_amount < 100:
        for i in range(5):
            play_sound('order_total_alert.mp3')
            time.sleep(3)

    print_package()
    back_home()
    return order_data


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


def scraper():

    site_connection()

    order_data = process_order()
    browser.quit()

if __name__ == '__main__':
    scraper()
