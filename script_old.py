from selenium import webdriver
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import logging
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

'''
https://sites.google.com/a/chromium.org/chromedriver/home
Check the above link for a guide on installing the chrome driver
'''

ORG_LINK = "https://www.linkedin.com/search/results/people/?facetCurrentCompany=%5B%223139%22%2C%2251686%22%5D&page="
DRIVER_PATH = "chromedriver.exe"
ORG_LINK_EC_ELEMENT = "search-s-facet__name t-16 t-black--light t-bold"
LINKEDIN = "https://www.linkedin.com"
LOGIN_LINK = "https://www.linkedin.com/uas/login"
LOGIN_EC_ELEMENT = "username"
LOGIN_USERNAME_ELEMENT = "username"
LOGIN_PASSWORD_ELEMENT = "password"
LOGIN_SUBMIT_ELEMENT = "//button[@type='submit']"  # CSS Selector
TIMEOUT = 360
PAGES = 100
PREDEFINED = False
LOGIN_USERNAME = ""
LOGIN_PASSWORD = ""
PROFILE_CLASS = "search-result__result-link ember-view"
PROFILE_EC = "pv-top-card-section__name"
PROFILE_NAME = "pv-top-card-section__name"
PROFILE_TITLE = "pv-top-card-section__headline"
PROFILE_COMPANY = "pv-top-card-v2-section__company-name"


class LinkedInScraper:
    def __init__(self):
        self.connected = False
        self.output = None
        self.excel = False

    def connect(self):
        logging.info("Starting Driver..")
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920x1080")
        self.driver = webdriver.Chrome(executable_path=DRIVER_PATH, chrome_options=chrome_options)
        logging.info("Logging IN")
        self.login()
        self.connected = True

    def login(self):
        if not self.connectPage(LOGIN_LINK, LOGIN_EC_ELEMENT, 'ID'):
            logging.error("Login Page Failed to load")
            raise Exception("Login Page Failed to Load, Please try again or correct the LOGIN_LINK VARIABLE")
        WebDriverWait(self.driver, 5)
        while True:
            username = self.driver.find_element_by_id(LOGIN_USERNAME_ELEMENT)
            password = self.driver.find_element_by_id(LOGIN_PASSWORD_ELEMENT)
            if PREDEFINED:
                your_user = LOGIN_USERNAME
                your_pass = LOGIN_PASSWORD
            else:
                your_user = input("Please enter your Linkedin username (EMAIL or Phone Number): ")
                your_pass = input("Please enter your Linkedin password: ")
            username.send_keys(your_user)
            password.send_keys(your_pass)
            login_attempt = self.driver.find_element_by_xpath(LOGIN_SUBMIT_ELEMENT)
            error_usr = self.driver.find_element_by_id("error-for-username")
            error_pss = self.driver.find_element_by_id("error-for-password")
            login_attempt.submit()
            print("CHECKING CREDENTIALS...")
            WebDriverWait(self.driver, 10)
            try:
                if error_usr.get_attribute("class").contains("hidden") and error_pss.get_attribute("class").contains("hidden"):
                    print("Correct Credentials")
                    logging.info("The login process is being finished")
                    WebDriverWait(self.driver, 10)
                    break
                else:
                    print("The Credentials were wrong")
                    if PREDEFINED:
                        print("ABORTING PROGRAM")
                        raise Exception("Wrong Credentials")
                    else:
                        print("Please re-enter the correct credentials")
            except StaleElementReferenceException:
                print("Correct Credentials")
                logging.info("The login process is being finished")
                WebDriverWait(self.driver, 10)
                break

    def connectPage(self, link, element, mode):
        try:
            self.driver.get(link)
            if mode == 'ID':
                element_present = EC.presence_of_element_located((By.ID, element))
            elif mode == 'CLASS':
                element_present = EC.presence_of_element_located((By.CLASS_NAME, element))
            else:
                logging.error("MODE INVALID")
                raise Exception("MODE must be either 'ID' or 'CLASS'. Aborting Program")
                exit(1)
            WebDriverWait(self.driver, TIMEOUT).until(element_present)
            return True
        except TimeoutException:
            logging.critical("Timed out waiting for page to load.. SKIPPING IT")
            return False

    def checkDriver(self):
        if not self.connected:
            logging.Error("The Script have to be connected first, have you used the connect function?")
            raise Exception("Error: not connected. Please connect first")
        if not self.excel:
            logging.Error("The excel file must be ready already, have you used the openFile function?")
            raise Exception("Error: Excel File not opened. Please open the excel file first")

    def clickLink(self, element, element_ec, mode, e_mode):
        self.checkDriver()
        logging.info("Clicking button : " + str(element))
        if e_mode:
            element.click()
        else:
            if mode == 'CLASS':
                self.driver.find_element_by_class_name(element).click()
            elif mode == 'ID':
                self.driver.find_element_by_id(element).click()
            else:
                logging.error("MODE INVALID")
                raise Exception("MODE must be either 'ID' or 'CLASS'. Aborting Program")
                exit(1)
        _element_ec = EC.presence_of_element_located((By.CLASS_NAME, element_ec))
        WebDriverWait(self.driver, TIMEOUT).until(_element_ec)

    def openFile(self, file):
        self.excel = True

    def WriteRow(self, row):
        print(str(row))

    def goBack(self, EC):
        pass

    def scrapeElement(self, element, mode):
        if mode == 'CLASS':
            e = EC.presence_of_element_located((By.CLASS_NAME, element))
        elif mode == 'ID':
            e = EC.presence_of_element_located((By.ID, element))
        else:
            raise Exception("Mode must be either CLASS or ID")
        WebDriverWait(self.driver, TIMEOUT).until(e)
        result = self.driver.get_elements_by_class_name(element) if mode == 'CLASS' else self.driver.get_elements_by_id(element)
        return result.text

    def scrapeProfile(self):
        name = self.scrapeElement(PROFILE_NAME, 'CLASS')
        title = self.scrapeElement(PROFILE_TITLE, 'CLASS')
        company = self.scrapeElement(PROFILE_COMPANY, 'CLASS')

        return [name, title, company]

    def scrapeOrg(self):
        self.checkDriver()
        for accum in range(1, PAGES + 1):
            logging.info("Connecting to page " + str(accum))
            org_link = ORG_LINK + str(accum)
            if not self.connectPage(org_link, ORG_LINK_EC_ELEMENT, 'CLASS'):
                continue
            profiles = self.driver.get_elements_by_class_name(PROFILE_CLASS)
            for profile in profiles:
                self.logging.info("Profile number " + str(profiles.index(profile)))
                self.clickLink(profile, PROFILE_EC, 'CLASS', True)
                profiledata = self.scrapeProfile()
                self.WriteRow(profiledata)
                self.driver.back()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} outfile.csv")
        exit(1)
    outfile = str(sys.argv[1])
    if not outfile.endswith(".csv"):
        raise Exception("the file must be in csv format. Make sure you added .csv as a suffix")

    print("Welcome to my script")
    print("By Mora Hannover")
    print("github.com/Mora-Hannover")
    print("Follow me on Instagram : @morahannover")
    logging.info("Script Started")
    scraper = LinkedInScraper()
    scraper.connect()
    scraper.openFile(outfile)
    scraper.scrapeOrg()
    logging.info("Script Finished")
    print("Thanks for using my script")
    print("I am Mora Hannover")
    print("github.com/Mora-Hannover")
    print("Follow me on Instagram : @morahannover")
    print("Check out my YT channel : youtube.com/c/morahannover")
