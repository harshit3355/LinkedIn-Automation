from selenium import webdriver
from dotenvy import load_env, read_file
from os import environ
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def start_browser():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get("https://www.linkedin.com/login")
    return driver

def login_to_linkedin(driver, email, password):
    try:
        username = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")
        username.send_keys(email)
        password_field.send_keys(password)
        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()
        time.sleep(5)
        print("Logged in successfully.")
    except Exception as e:
        print(f"Login failed: {e}")
        driver.quit()
        return None
    return driver

def send_connection_requests(driver):
    try:
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[contains(@class, 'search-global-typeahead__input')]"))
        )
        search_box.clear()
        search_box.send_keys("DevOps Engineer")
        search_box.send_keys(Keys.RETURN)
        time.sleep(5)

        people_tab = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'People')]"))
        )
        people_tab.click()
        print("Navigated to the 'People' section successfully.")
        time.sleep(5)

        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)

            connect_buttons = driver.find_elements(By.XPATH, "//button[.//span[contains(@class, 'artdeco-button__text') and text()='Connect']]")
            if not connect_buttons:
                if not go_to_next_page(driver):
                    break
                continue

            for button in connect_buttons:
                try:
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                    time.sleep(1)
                    close_existing_popups(driver)  # Ensure no pop-ups are blocking
                    driver.execute_script("arguments[0].click();", button)  # Use JS click
                    time.sleep(2)

                    if handle_connection_modal(driver, button):
                        print("Connection request sent successfully.")
                    else:
                        print("Retrying with 'Send without a note'.")
                        close_existing_popups(driver)
                        time.sleep(1)
                        button.click()
                        time.sleep(2)
                        send_without_note(driver)
                except Exception as e:
                        print(f"Error clicking 'Connect' button: {e}")
                        close_existing_popups(driver)
            if not go_to_next_page(driver):
                break
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        driver.quit()

def handle_connection_modal(driver, button):
    try:
        time.sleep(2)

        if is_limit_reached(driver):
            print("Note limit reached. Closing modal.")
            close_existing_popups(driver)
            return False

        add_note_button = WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Add a note']]"))
        )
        add_note_button.click()
        time.sleep(2)

        note_textarea = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, "//textarea[@name='message']"))
        )
        note_textarea.send_keys("Hi, I'd like to connect with you!")

        send_button = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Send']]"))
        )
        send_button.click()
        time.sleep(2)
        return True
    except:
        return False

def send_without_note(driver):
    try:
        send_without_note_button = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Send without a note']]"))
        )
        send_without_note_button.click()
        time.sleep(2)
        print("Connection request sent without a note.")
    except:
        print("Failed to send connection request.")

def is_limit_reached(driver):
    try:
        limit_message = driver.find_element(By.XPATH, "//p[contains(text(), 'No free personalized invitations left')]")
        return True if limit_message else False
    except:
        return False

def close_existing_popups(driver):
    try:
        popups = driver.find_elements(By.XPATH, "//button[contains(@class, 'artdeco-modal__dismiss')]")
        for popup in popups:
            popup.click()
            time.sleep(1)
    except:
        pass

def go_to_next_page(driver):
    try:
        next_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, 'Next')]")
                                       ))
        next_button.click()
        time.sleep(5)
        return True
    except:
        return False

if __name__ == "__main__":
    load_env(read_file('.env'))
    email = environ.get('EMAIL')
    password = environ.get('PASSWORD')
    while True:
        try:
            driver = start_browser()
            driver = login_to_linkedin(driver, email, password)
            if driver:
                send_connection_requests(driver)
            print("Restarting the browser...\n")
            time.sleep(30)
        except Exception as e:
            print(f"Main loop error: {e}")
            time.sleep(60)
