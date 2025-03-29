import asyncio

from selenium.common import NoSuchElementException, TimeoutException, ElementClickInterceptedException
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
from googletrans import Translator
from collections import Counter

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# The webdriver management will be handled by the browserstack-sdk
# so this will be overridden and tests will run browserstack -
# without any changes to the test files!
options = ChromeOptions()
options.set_capability('sessionName', 'BStack Sample Test')
driver = webdriver.Chrome(options=options)
driver.maximize_window()


def click_element(driver, xpath, timeout=10):
    try:
        # Wait for the element to be present
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )

        # Scroll the element into view
        driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", element)

        # Wait for the element to be clickable
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )

        # Click the element
        element.click()
    except TimeoutException:
        print(f"Element with xpath {xpath} not found within {timeout} seconds.")
    except ElementClickInterceptedException:
        print(f"Element with xpath {xpath} was not clickable due to being intercepted.")
    except NoSuchElementException:
        print(f"Element with xpath {xpath} does not exist on the page.")
def handle_accept_button(driver):
    try:
        # Attempt to click the accept button if it exists
        accept_button = driver.find_element(By.XPATH, "//button[@id='didomi-notice-agree-button']")
        accept_button.click()
    except NoSuchElementException:
        # If the button is not present, continue without error
        print("Accept button not present, continuing without clicking.")


async def translate_titles(titles):
    translator = Translator()
    translated_titles = []
    for title in titles:
        translated_title = await translator.translate(title, src='es', dest='en')
        translated_titles.append(translated_title.text)
    return translated_titles



try:
    # Visit El País website
    driver.get("https://elpais.com/")
    print("Website loaded in Spanish.")

    # Navigate to the Opinion section
    handle_accept_button(driver)
    click_element(driver, "//a[@cmp-ltrk='portada_menu'][normalize-space()='Opinión']")
    click_element(driver, "//*[contains(text(), 'ACCEPT AND CONTINUE')]")
    click_element(driver, "//button[@id='btn_open_hamburger']//*[name()='svg']")
    click_element(driver, "//a[@cmp-ltrk='header_hamburguesa'][normalize-space()='Opinión']")
    print("Clicked on opinion.")

    # Fetch the first five articles
    articles = driver.find_elements(By.CSS_SELECTOR, "article")
    titles = []
    contents = []
    images = []

    for article in articles:
        if len(titles) >= 5:
            break  # Exit the loop once we have five titles

        try:
            title = article.find_element(By.TAG_NAME, "h2").text
            if title:  # Check if the title is not empty
                titles.append(title)
                try:
                    content = article.find_element(By.TAG_NAME, "p").text
                except NoSuchElementException:
                    content = "No content available"

                # Locate the image element within the article
                try:
                    image = article.find_element(By.CSS_SELECTOR, "img").get_attribute("src")
                except NoSuchElementException:
                    image = None

                contents.append(content)
                images.append(image)

                print(f"Article Title: {title}")
                print(f"Content: {content}")

                # Download and save the cover image if image exists
                if image:
                    img_data = requests.get(image).content
                    # Create a valid filename by replacing invalid characters
                    valid_title = "".join(c for c in title if c.isalnum() or c in (' ', '_')).rstrip()
                    with open(f"{valid_title}.jpg", 'wb') as handler:
                        handler.write(img_data)
        except NoSuchElementException:
            continue

    # Translate Article Headers
    translated_titles = asyncio.run(translate_titles(titles))

    for translated_title in translated_titles:
        print(f"Translated Title: {translated_title}")

    # Analyze Translated Headers
    all_words = ' '.join(translated_titles).lower().split()
    word_count = Counter(all_words)
    repeated_words = {word: count for word, count in word_count.items() if count > 2}

    print(f"Repeated words: {repeated_words}")

finally:
    # Stop the driver
    driver.quit()


# If hamberbureger exists click on it
# hamburger_menu = "//button[@id='btn_open_hamburger']//*[name()='svg']"
# scroll to //a[@cmp-ltrk='header_hamburguesa'][normalize-space()='Opinión']