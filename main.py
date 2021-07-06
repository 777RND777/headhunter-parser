from concurrent.futures import ThreadPoolExecutor
from kzt_exchangerates import Rates
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import config
import re


def get_currency(currency):
    if not currency.isdigit():
        if currency.startswith("руб"):
            return "RUB"
        elif currency == "$":
            return "USD"
        elif currency == "€":
            return "EUR"
        else:
            return currency.upper()
    return "KZT"


class Salary:
    top_value = 0
    bot_value = 0
    kzt = 0

    def __init__(self, info):
        self.currency = get_currency(info.split()[-1])
        salary_range = [int(i.replace(" ", "")) for i in re.findall(r"\d+ \d+", info)]
        if not salary_range:
            salary_range = [int(i.replace(" ", "")) for i in re.findall(r"\d+", info)]
            if not salary_range:
                return

        if len(salary_range) == 1:
            self.top_value = salary_range[0]
            self.kzt = self.to_kzt(self.top_value)
            return

        # actual range
        self.bot_value = salary_range[0]
        self.top_value = salary_range[1]
        self.kzt = self.to_kzt(self.bot_value)

    def __str__(self):
        if not self.top_value:
            output = f"{self.bot_value:,} {self.currency}"
            if self.currency != "KZT":
                output += f" ({self.kzt:,} в KZT)"
            return output

        output = f"{self.bot_value:,} - {self.top_value:,} {self.currency}"
        if self.currency != "KZT":
            output += f" ({self.kzt:,} - {self.to_kzt(self.top_value):,} в KZT)"
        return output

    def to_kzt(self, value):
        return value * round(rates.get_exchange_rate(self.currency, 'KZT'))


def vacancy_processing(v):
    link = v.find_element_by_tag_name("a")
    name = link.text
    for word in config.AVOID_WORDS:
        if word in name.lower():
            return

    salary_info = v.find_element_by_class_name("vacancy-serp-item__sidebar").text
    if not salary_info:
        return

    salary = Salary(salary_info)
    if salary.kzt < config.MINIMUM_SALARY:
        return

    print(f'''
Название:   {name}
Оклад:      {salary}
Ссылка:     {link.get_attribute('href')}''')


def get_next_page():
    next_page = driver.find_element_by_css_selector("a.bloko-button.HH-Pager-Controls-Next.HH-Pager-Control")
    url = next_page.get_attribute("href")
    page_collector(url)


def page_collector(url):
    driver.get(url)
    table = driver.find_element_by_class_name("vacancy-serp")
    with ThreadPoolExecutor() as executor:
        try:
            executor.map(vacancy_processing, table.find_elements_by_css_selector("div.vacancy-serp-item"))
        except NoSuchElementException:
            pass

    try:
        get_next_page()
    except NoSuchElementException:
        pass


if __name__ == "__main__":
    rates = Rates()
    options = webdriver.ChromeOptions()
    options.headless = True
    driver = webdriver.Chrome("chromedriver.exe", options=options)
    page_collector(config.START_PAGE)
    driver.quit()
