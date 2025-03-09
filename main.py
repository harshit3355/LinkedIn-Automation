from selenium import webdriver
from dotenvy import load_env, read_file
from os import environ
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

def start_browser():
    """Function to start a new browser session."""
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get("https://www.linkedin.com/login")
    return driver

# Function to log in to LinkedIn
def login_to_linkedin(driver, email, password):
    """Function to log in to LinkedIn."""
    try:
        username = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")
        username.send_keys(email)
        password_field.send_keys(password)

        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()
        time.sleep(3)
        print("Logged in successfully.")
    except Exception as e:
        print(f"Login failed: {e}")
        driver.quit()
        return None
    return driver

# Function to send connection requests
def send_connection_requests(driver):
    """Function to search for people and send connection requests."""
    try:
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[contains(@class, 'search-global-typeahead__input')]"))
        )
        search_box.clear()
        search_box.send_keys("Devops Engineer")
        search_box.send_keys(Keys.RETURN)
        time.sleep(5)

        # Navigate to "People" tab
        try:
            people_tab = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'People')]"))
            )
            people_tab.click()
            print("Navigated to the 'People' section successfully.")
            time.sleep(5)
        except Exception as e:
            print(f"Error navigating to 'People': {e}")
            return

        while True:  # Keep processing profiles across multiple pages
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)

            connect_buttons = driver.find_elements(By.XPATH, "//button[.//span[contains(@class, 'artdeco-button__text') and text()='Connect']]")

            if not connect_buttons:
                print("No 'Connect' buttons found. Moving to the next page...")
                if not go_to_next_page(driver):
                    print("No more pages left. Exiting.")
                    break
                continue  # Move to next iteration

            for button in connect_buttons:
                try:
                    driver.execute_script("arguments[0].scrollIntoView(true);", button)
                    time.sleep(1)

                    try:
                        button.click()
                    except:
                        driver.execute_script("arguments[0].click();", button)

                    time.sleep(2)

                    # First, try sending a connection request with a note
                    try:
                        add_note_button = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Add a note']]"))
                        )
                        add_note_button.click()
                        time.sleep(2)

                        note_box = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, "//textarea[@name='message']"))
                        )
                        note_box.send_keys("Hello, I'd love to connect with you!")
                        time.sleep(1)

                        # Clicking the correct "Send Invitation" button
                        send_invitation_button = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Send invitation']"))
                        )
                        send_invitation_button.click()
                        print("Connection request sent with a note.")
                        time.sleep(2)
                        continue  # Move to next profile

                    except Exception:
                        print("No option to add a note. Sending without a note.")

                    # If adding a note isn't possible, send without a note
                    try:
                        send_without_note_button = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Send without a note']]"))
                        )
                        send_without_note_button.click()
                        print("Connection request sent successfully (without note).")
                        time.sleep(2)
                    except Exception as send_error:
                        print(f"Error finding 'Send without a note' button: {send_error}")

                except Exception as button_error:
                    print(f"Error clicking 'Connect' button: {button_error}")

            # After processing all profiles, move to the next page
            if not go_to_next_page(driver):
                print("No more pages left. Exiting.")
                break

    except KeyboardInterrupt:
        print("Script stopped by user.")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        driver.quit()

# Function to navigate to the next page
def go_to_next_page(driver):
    """Attempts to navigate to the next page. Returns True if successful, False if no more pages exist."""
    try:
        next_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, 'Next')]"))
        )
        next_button.click()
        time.sleep(5)
        print("Moved to the next page.")
        return True
    except Exception:
        print("No more pages available.")
        return False

if __name__ == "__main__":
    load_env(read_file('.env'))
    email=environ.get('EMAIL')
    password=environ.get('PASSWORD')
    while True:
        try:
            driver = start_browser()
            email = email  # Replace with your LinkedIn email
            password = password  # Replace with your LinkedIn password
            driver = login_to_linkedin(driver, email, password)

            if driver:
                send_connection_requests(driver)

            print("Restarting the browser...\n")
            time.sleep(30)  # Delay before restarting to avoid detection

        except Exception as main_error:
            print(f"Main loop error: {main_error}")
            time.sleep(60)  # Wait before restarting if an error occurs
