import time
from selenium import webdriver
from selenium.webdriver.support import expected_conditions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from fake_useragent import UserAgent
from selenium.webdriver.common.action_chains import ActionChains
from pprint import pprint
import json


def wait_element(browser, delay_second=1, by=By.TAG_NAME, value=None):
    return WebDriverWait(browser, delay_second).until(
        expected_conditions.presence_of_element_located((by, value)))


def vacancy_page(browser):
    try:
        vacancy_list = wait_element(browser, delay_second=1, by=By.ID, value="a11y-main-content")
        vacancy_tags = vacancy_list.find_elements(By.CLASS_NAME, value="serp-item")
        for vacancy_tag in vacancy_tags:
            link_tag = wait_element(vacancy_tag, delay_second=1, by=By.CLASS_NAME, value="serp-item__title")
            vacancy_link = link_tag.get_attribute("href")
            emp_city_tag = vacancy_tag.find_elements(By.CLASS_NAME, value="bloko-text")
            emp_city_list = []
            for data_attributes in emp_city_tag:
                emp_city_attr = data_attributes.text.strip()
                emp_city_list.append(emp_city_attr)
            employer = emp_city_list[0]
            city = emp_city_list[1].split(",")[0]
            salary_list = []
            salary_tag = vacancy_tag.find_elements(By.CLASS_NAME, value="bloko-header-section-2")
            for salary_attributes in salary_tag:
                salary_attr = salary_attributes.text.strip().replace("\u202f", " ")
                salary_list.append(salary_attr)
            salary = ','.join(salary_list)
            vacancy_data.append({
                "vacancy_link": vacancy_link,
                "employer": employer,
                "city": city,
                "salary": salary
            })
    except Exception as ex:
        print(ex)


useragent = UserAgent()
chrome_webdriver_path = ChromeDriverManager().install()
options = webdriver.ChromeOptions()
options.add_argument(f'user-agent={useragent.random}')
#options.add_argument('--headless') #без запуска браузера
#options.add_argument('--incognito') #режим инкогнито
browser_service = Service(executable_path=chrome_webdriver_path)
browser = Chrome(service=browser_service, options=options)
actions = ActionChains(browser)

browser.get("https://spb.hh.ru/search/vacancy?area=1&area=2&ored_clusters"
            "=true&text=NAME%3A%28python%29+AND+DESCRIPTION%3A"
            "%28Django+OR+Flask%29&search_period=7")

vacancy_data = []
vacancy_tags = []


def pars_hh():
    try:
        wait_element(browser, delay_second=1, by=By.ID, value="a11y-main-content")

        buttons_check = browser.find_elements(By.CLASS_NAME, value='pager') #Проверяем наличие страниц

        browser.find_element(by=By.XPATH, value='// button[@data-qa="cookies-policy-informer-accept"]').click()

        if buttons_check:
            buttons = wait_element(browser, delay_second=1, by=By.CLASS_NAME, value='pager')
            buttons_list = buttons.find_elements(by=By.XPATH, value='//a[@data-qa="pager-page"]')
            print(buttons_list)
            for button in buttons_list:
                vacancy_page(browser)
                actions.click(button).perform()
                time.sleep(5)
                print(browser.current_url)
            vacancy_page(browser)
        else:
            vacancy_page(browser)
    except Exception as ex:
        print(ex)


if __name__ == '__main__':
    pars_hh()
    pprint(len(vacancy_data))
    pprint(vacancy_data)
    browser.close()
    browser.quit()
    with open('result.json', 'w') as f:
        json.dump(vacancy_data, f)
