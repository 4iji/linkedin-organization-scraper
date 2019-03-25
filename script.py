from subprocess import check_call
from datetime import datetime
import csv
import os, os.path
import re
import argparse

parser = argparse.ArgumentParser(description='Extract Linkedin')
parser.add_argument('outfile', metavar='outfile.csv', type=str , help='Output file, must end in .csv')
parser.add_argument('filterlink', metavar='https://www.linkedin.com/search/results/people/?facetCurrentCompany=%5B%223139%22%2C%2251686%22%5D', type=str , help='the link of the search filter')
parser.add_argument('mode', metavar='w', type=str , help='w to overwrite the csv, a to append the csv')
args = parser.parse_args()

#ORG_LINK = "https://www.linkedin.com/search/results/people/?facetCurrentCompany=%5B%223139%22%2C%2251686%22%5D&page="
PAGE_ARG = "&page="
ORG_LINK = args.filterlink + PAGE_ARG if not PAGE_ARG in args.filterlink else args.filterlink
MODE = args.mode
assert MODE in ['w', 'a']
DRIVER_PATH = "chromedriver.exe"
ORG_LINK_EC_ELEMENT = "search-s-facet__name"
LINKEDIN = "https://www.linkedin.com"
LOGIN_LINK = "https://www.linkedin.com/uas/login"
LOGIN_EC_ELEMENT = "username"
LOGIN_USERNAME_ELEMENT = "username"
LOGIN_PASSWORD_ELEMENT = "password"
LOGGED_IN = "https://www.linkedin.com/feed/"
LOGIN_SUBMIT_ELEMENT = "//button[@type='submit']"  # CSS Selector
TIMEOUT = 360
PAGES = 100
PREDEFINED = False
LOGIN_USERNAME = ""
LOGIN_PASSWORD = ""
PROFILE_CLASS = "search-result__result-link"
PROFILE_EC = "pv-top-card-section__name"
PROFILE_NAME = "pv-top-card-section__name"
PROFILE_TITLE = "pv-top-card-section__headline"
PROFILE_COMPANY = "pv-top-card-v2-section__company-name"
LINKEDIN = "https://www.linkedin.com"
OUTFILE = args.outfile
ENCODE= "utf-8"
ACTOR_NAME_XPATH = '//span[@class="actor-name"]'
ACTOR = 'actor-name'
BROKEN_PROFILE = "LinkedIn Member"


try:
    from selenium import webdriver
    from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import NoSuchElementException
except ImportError:
    check_call(["pip", "install" , "-r" , "requirements.txt"])


def export_csv(df):
    with open(OUTFILE, 'w', newline='', encoding=ENCODE) as csvfile:
        writer = csv.writer(csvfile)
        for row in df:
            pass #writer.writerow(row)


def launch_selenium():
    chrome_options = Options()
    #chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")
    #chrome_options.add_argument(f"user-data-dir=C:\\Users\\{os.path.split(os.path.expanduser('~'))[-1]}\\AppData\\Local\\Google\\Chrome\\User Data")
    chrome_options.add_argument(f"user-data-dir=data")
    #chrome_driver = os.getcwd() +"\\chromedriver.exe"
    #driver = webdriver.Chrome(options=chrome_options, executable_path=chrome_driver)
    driver = webdriver.Chrome()
    return driver

def connectPage(driver, link, element, mode):
    print("Connecting to", link)
    driver.get(link)
    if mode == 'ID':
        element_present = EC.presence_of_element_located((By.ID, element))
    elif mode == 'CLASS':
        element_present = EC.presence_of_element_located((By.CLASS_NAME, element))
    else:
        print("MODE INVALID")
        raise Exception("MODE must be either 'ID' or 'CLASS'. Aborting Program")
    WebDriverWait(driver, TIMEOUT).until(element_present)

def WaitForPage(driver, element, mode):
    if mode == 'ID':
        element_present = EC.presence_of_element_located((By.ID, element))
    elif mode == 'CLASS':
        element_present = EC.presence_of_element_located((By.CLASS_NAME, element))
    elif mode == 'CSS':
        element_present = EC.presence_of_element_located((By.CSS_SELECTOR, element))
    else:
        print("MODE INVALID")
        raise Exception("MODE must be either 'ID' or 'CLASS'. Aborting Program")
    WebDriverWait(driver, TIMEOUT).until(element_present)

def checkLink(driver, url):
    return driver.current_url == url

def scrapeElement(driver, element, mode):
        if mode == 'CLASS':
            e = EC.presence_of_element_located((By.CLASS_NAME, element))
        elif mode == 'ID':
            e = EC.presence_of_element_located((By.ID, element))
        else:
            raise Exception("Mode must be either CLASS or ID")
        WebDriverWait(driver, TIMEOUT).until(e)
        result = driver.find_element_by_class_name(element) if mode == 'CLASS' else driver.find_element_by_id(element)
        return result.text

def scrapeProfile(driver):
    name = scrapeElement(driver, PROFILE_NAME, 'CLASS')
    title = scrapeElement(driver, PROFILE_TITLE, 'CLASS')
    company = scrapeElement(driver, PROFILE_COMPANY, 'CLASS')

    return [name, title, company]

def clickLink(driver, element, element_ec, mode, e_mode):
    print("Clicking button : " + str(element))
    if e_mode:
        element.click()
    else:
        if mode == 'CLASS':
            driver.find_element_by_class_name(element).click()
        elif mode == 'ID':
            driver.find_element_by_id(element).click()
        else:
            print("MODE INVALID")
            raise Exception("MODE must be either 'ID' or 'CLASS'. Aborting Program")
    _element_ec = EC.presence_of_element_located((By.CLASS_NAME, element_ec))
    WebDriverWait(driver, TIMEOUT).until(_element_ec)

def getElementTextByClass(driver, y, element):
    try:
        element_present = EC.presence_of_element_located((By.CLASS_NAME, element))
        WebDriverWait(driver, TIMEOUT).until(element_present)
        out = y.find_element_by_class_name(element).text
        print(out)
        return out
    except NoSuchElementException:
        print('ignoring')
        return ''



if __name__ == "__main__":
    print("START")

    driver = launch_selenium()
    print("Launched Selenium")

    #LOG IN
    connectPage(driver, LOGIN_LINK, LOGIN_EC_ELEMENT, 'ID')
    print("PLEASE LOG IN")

    #WAIT FOR LOG IN
    WebDriverWait(driver, TIMEOUT).until(lambda d: d.current_url == LOGGED_IN)
    print("LOGGED IN")

    #df = []
    if MODE == 'a':
        try:
            csvfile = open(OUTFILE, 'r', newline='', encoding=ENCODE)
            reader = csv.reader(csvfile)
            profiles_done = [row[-1] for row in reader]
            csvfile.close()
            csvfile = open(OUTFILE, 'a', newline='', encoding=ENCODE)
        except FileNotFoundError:
            csvfile = open(OUTFILE, 'w', newline='', encoding=ENCODE)
            profiles_done = []
    elif MODE == 'w':
        csvfile = open(OUTFILE, 'w', newline='', encoding=ENCODE)
        profiles_done = []
    else:
        raise Exception("Mode must be wither w or a")
    writer = csv.writer(csvfile)

    #START SCRAPING
    for accum in range(1, PAGES + 1):
        print("Page", accum)
        org_link = ORG_LINK + str(accum)
        connectPage(driver, org_link, ORG_LINK_EC_ELEMENT, 'CLASS')
        print("filtering")
        profiles_elements = driver.find_elements_by_class_name(PROFILE_CLASS)
        profiles_elements = list(filter(lambda x : getElementTextByClass(driver, x, ACTOR) != BROKEN_PROFILE, profiles_elements))
        profiles = [p.get_attribute('href') for p in profiles_elements if not p.get_attribute('href').endswith('#')]
        profiles = list(set(profiles))
        print(profiles)
        for profile in profiles:
            print("Profile number " + str(profiles.index(profile)))
            if profile in profiles_done:
                print("availabe. continuing")
                continue
            connectPage(driver, profile, PROFILE_EC, 'CLASS')
            profiledata = scrapeProfile(driver)
            profiledata.append(profile)
            print(profiledata)
            writer.writerow(profiledata)
    
    #export_csv(df)

    print("DONE")