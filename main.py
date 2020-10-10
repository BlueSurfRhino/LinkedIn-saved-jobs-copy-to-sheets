import datetime
import time
import gspread 
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from rocreds import *

def main():
    LINKEDIN_LOGIN_URL = 'https://www.linkedin.com/login'
    LINKEDIN_SAVED_JOBS_URL = 'https://www.linkedin.com/my-items/saved-jobs/?cardType=SAVED'

    # Log into LinkedIn
    driver = webdriver.Chrome()
    driver.get(LINKEDIN_LOGIN_URL)
    username = driver.find_element_by_id('username')
    username.send_keys(RO_ADDR)
    page = driver.page_source
    pwlogin = driver.find_element_by_id('password')
    pwlogin.send_keys(RO_PW)
    # Click the login button (there's only one!)
    submitBtn = driver.find_element_by_class_name('btn__primary--large')
    submitBtn.click()
    # Go to saved jobs listing page
    driver.get(LINKEDIN_SAVED_JOBS_URL)
    # Need to grab the actual page content w/ Selenium since requests &
    # Beautiful doesn't see the html unless the javascript code has run
    time.sleep(2)
    page = driver.page_source
    # Be a good citizen and leave
    driver.quit()
    # Soup-time!  Find all the saved jobs
    soup = BeautifulSoup(page, 'html.parser')
    savedJobsList = soup.find_all('div', class_='entity-result__item')
    # Login into our Google Sheet and get our worksheet (ws)
    gc = gspread.service_account(filename='creds.json')
    sh = gc.open_by_key(RO_SHEET)
    ws = sh.sheet1
    # Go through each job listing and write the info to our worksheet
    today = datetime.date.today().strftime('%-m/%d/%y')
    for job in savedJobsList:
        reportLine = []
        # date
        reportLine.append(today)
        # company
        companyName = job.find('div', class_='entity-result__primary-subtitle')
        reportLine.append(companyName.text.strip('\n'))
        # job title
        jobTitleAndLink = job.find_all('a', class_='app-aware-link', href=True)
        reportLine.append(jobTitleAndLink[1].text.strip('\n'))
        # link
        reportLine.append(jobTitleAndLink[1].get('href').split('?')[0])
        # add row to end of sheet
        ws.append_row(reportLine,value_input_option='USER_ENTERED')
        print(reportLine)

if __name__ == "__main__":
    main()
