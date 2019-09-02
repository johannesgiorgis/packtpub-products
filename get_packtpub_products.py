import datetime
import logging
import os
from time import sleep

import pandas as pd
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# set logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# create handler
c_handler = logging.StreamHandler()
c_handler.setLevel(logging.INFO)

# Create formatters and add it to handlers
LOG_FORMAT = "[%(asctime)s - %(levelname)s - %(module)s:%(lineno)5s ] %(message)s"
c_format = logging.Formatter(LOG_FORMAT)
c_handler.setFormatter(c_format)

# Add handlers to the logger
logger.addHandler(c_handler)

PACKTPUB_PRODUCTS_URL = "https://account.packtpub.com/account/products"


def getCredentials():
    '''
    returns email address and password
    '''
    logger.info("Getting credentials...")
    load_dotenv()

    if "EMAIL" not in os.environ or "PASSWORD" not in os.environ:
        logger.error("Credentials are not present!")
        raise Exception("Please add EMAIL and PASSWORD to environment variables!")
        sys.exit(1)

    email = os.getenv("EMAIL")
    password = os.getenv("PASSWORD")
    logger.info("Completed getting credentials")
    return email, password


def login():
    """
    login to the packtpub web page
    """
    logger.info("Logging in...")

    email, password = getCredentials()

    chrome_driver = "/usr/bin/chromedriver"
    browser = webdriver.Chrome(executable_path=chrome_driver)
    browser.get(PACKTPUB_PRODUCTS_URL)

    delay = 30  # seconds
    try:
        username_input = WebDriverWait(browser, delay).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "/html/body/app-root/div/ng-component/div/div/ng-component/div/form/div[1]/input",
                )
            )
        )
        logger.info("Login Page is ready!")
    except TimeoutException:
        logger.exception("Loading Login Page took too much time!")

    password_input = browser.find_element_by_xpath(
        "/html/body/app-root/div/ng-component/div/div/ng-component/div/form/div[2]/input"
    )

    username_input.send_keys(email)
    password_input.send_keys(password)

    login_button = browser.find_element_by_xpath(
        "/html/body/app-root/div/ng-component/div/div/ng-component/div/form/button"
    )
    login_button.click()
    logger.info("Logged in")
    return browser


def get_products_list(browser):
    """
    get list of products
    """
    logger.info("Getting products list...")
    my_products = []
    next_page_exists = True
    page_number = 1
    delay = 30  # seconds
    xml_path = "/html/body/app-root/div/ng-component/div/mat-sidenav-container/mat-sidenav-content/account-products/div/div/mat-paginator/div/div[2]/button[3]"

    while next_page_exists:

        try:
            myElem = WebDriverWait(browser, delay).until(
                EC.presence_of_element_located((By.XPATH, xml_path))
            )
            logger.info(f"Products Page {page_number} is ready!")

        except TimeoutException:
            logger.exception(f"Loading Products Page {page_number} took too much time!")

        # allow us to capture new html content
        sleep(3)

        soup_level = BeautifulSoup(browser.page_source, "html.parser")

        page_products = []

        for product_title in soup_level.find_all("h5"):
            page_products.append(product_title.text)

        logger.info(f"{page_products}")
        my_products.extend(page_products)

        sleep(1)

        next_page_link = browser.find_element_by_xpath(xml_path)

        logger.info(
            f"Next Page Displayed:'{next_page_link.is_displayed()}'\tNext Page Enabled:'{next_page_link.is_enabled()}'"
        )

        next_page_exists = next_page_link.is_enabled()

        logger.info("Getting next page...")
        page_number += 1
        browser.execute_script("arguments[0].click();", next_page_link)

    logger.info(f"Completed going through all {len(my_products)} products!")
    return my_products


def get_packtpub_products_list():
    """
    get packtpub products list
    """
    logger.info("Getting packtpub owned products list...")
    browser = login()
    packtpub_products = get_products_list(browser)
    browser.quit()
    logger.info("Completed getting packtpub owned products list")
    return packtpub_products


def get_mock_data_products_list():
    """
    mock data products list
    """
    logger.info("Getting products test data...")
    products_list = [
        "Pandas Cookbook",
        "Django by Example [Video]",
        "Learning Python [Video]",
        "Implementing Modern DevOps",
        "Software Architecture with Python [Video]",
        "Cloud Native programming with Golang",
        "DevOps with Kubernetes",
        "Ethical Hacking for Beginners [Video]",
        "Hands - On Reinforcement Learning with Python [Video]",
        "Network Programming with Go [Video]",
    ]
    return products_list


def convert_products_list_to_df(products_list):
    """
    converts list of products into dataframe
    """
    logger.info("Converting list of products into dataframe...")
    list_of_lists = []
    for product in products_list:
        list_of_lists.append([product])

    products_df = pd.DataFrame(list_of_lists, columns=["product"])
    logger.info("Completed converting list of products into dataframe")
    return products_df


def format_dataframe(df):
    """
    format and clean dataframe into 2 columns
        - product
        - type
    """
    logger.info("Formatting dataframe...")
    df = df["product"].str.split("[", expand=True)
    df.columns = ["product", "type"]
    df.loc[df["type"].isnull(), "type"] = "Book"
    df["type"] = df["type"].str.replace("]", "")
    df["product"] = df["product"].str.rstrip()
    logger.info("Completed formatting dataframe")
    return df


def save_df_to_csv(df):
    """
    save dataframe as csv file
    """
    logger.info("Saving dataframe as a csv file...")
    now = datetime.datetime.now()
    csv_dir = ""
    csv_file_name = now.strftime("%F") + "-packt-pub-products-library.csv"
    csv_file_full_path = csv_dir + csv_file_name
    logger.info(f"Saving to '{csv_file_full_path}'")
    df.to_csv(csv_file_full_path)
    logger.info("Completed saving dataframe as a csv file")


if __name__ == "__main__":
    logger.info("Program Started")
    my_products = get_packtpub_products_list()
    # my_products = get_mock_data_products_list()
    products_df = convert_products_list_to_df(my_products)
    products_df = format_dataframe(products_df)
    save_df_to_csv(products_df)
    logger.info("Program Completed")
