import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup

from dotenv import load_dotenv

load_dotenv()

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

PACKTPUB_PRODUCTS_URL = "https://account.packtpub.com/account/products"


chrome_driver = "/usr/bin/chromedriver"

browser = webdriver.Chrome(executable_path=chrome_driver)  # Or Chrome(), or Ie(), or Opera()
browser.get(LOGIN_URL)

delay = 30  # seconds
try:
    myElem = WebDriverWait(browser, delay).until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                "/html/body/app-root/div/ng-component/div/div/ng-component/div/form/div[1]/input",
            )
        )
    )
    print("Login Page is ready!")
except TimeoutException:
    print("Loading took too much time!")

username = browser.find_element_by_xpath(
    "/html/body/app-root/div/ng-component/div/div/ng-component/div/form/div[1]/input"
)
password = browser.find_element_by_xpath(
    "/html/body/app-root/div/ng-component/div/div/ng-component/div/form/div[2]/input"
)

username.send_keys(EMAIL)
password.send_keys(PASSWORD)

login_button = browser.find_element_by_xpath(
    "/html/body/app-root/div/ng-component/div/div/ng-component/div/form/button"
)
login_button.click()

# print("\nPage Source:")
# print(browser.page_source)

# browser.implicitly_wait(10)

xml_path = "/html/body/app-root/div/ng-component/div/mat-sidenav-container/mat-sidenav-content/account-products/div/div/div[2]/account-product-details[1]/div/div/div[2]/div/div[2]/a/span"

xml_path = "/html/body/app-root/div/ng-component/div/mat-sidenav-container/mat-sidenav-content/account-products/div/div/div[2]/account-product-details[10]/div/div/div[2]/div/div[2]/a/span"

# delay = 10  # seconds
try:
    myElem = WebDriverWait(browser, delay).until(
        EC.presence_of_element_located((By.XPATH, xml_path))
    )
    print("Products Page is ready!")
except TimeoutException:
    print("Loading took too much time!")

soup_level1 = BeautifulSoup(browser.page_source, "html.parser")

for link in soup_level1.find_all("h5"):
    print(f"\t{link}|{link.text}")


print("\n\n")

xml_path = "/html/body/app-root/div/ng-component/div/mat-sidenav-container/mat-sidenav-content/account-products/div/div/mat-paginator/div/div[2]/button[3]/span/svg"

xml_path = "/html/body/app-root/div/ng-component/div/mat-sidenav-container/mat-sidenav-content/account-products/div/div/mat-paginator/div/div[2]/button[3]"


next_page_link = browser.find_element_by_css_selector('[aria-label="Next page"]')
# browser.find_element_by_xpath(xml_path)
print(f"Naving to navigate page - '{next_page_link}'")
next_page_link.click()

print("\n\n")
# for i in range(20):
#    next_page_link = browser.find_element_by_xpath(
#        "/html/body/app-root/div/ng-component/div/mat-sidenav-container/mat-sidenav-content/account-products/div/div/mat-paginator/div/div[2]/button[3]/span/svg"
#    )
#    print(f"{i} - Naving to navigate page - '{next_page_link}'")
#    next_page_link.click()
