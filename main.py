from consts import *
from kzt_exchangerates import Rates
from selenium.common import exceptions
from selenium import webdriver


class Salary:
    top_value = 0
    bot_value = 0
    currency = "KZT"
    kzt = 0

    def __init__(self, info):
        info = info.split("-")
        if len(info) == 1:
            self.strict_parse(info[0].split())
            self.kzt = self.to_kzt(self.top_value)
        else:
            self.range_parse(info)
            self.kzt = self.to_kzt(self.bot_value)

    def __str__(self):
        if not self.bot_value:
            output = f"{self.top_value:,} {self.currency}"
            if self.currency != "KZT":
                output += f" ({self.kzt:,} в KZT)"
        else:
            output = f"{self.bot_value:,} - {self.top_value:,} {self.currency}"
            if self.currency != "KZT":
                output += f" ({self.kzt:,} - {self.to_kzt(self.top_value):,} в KZT)"
        return output

    def strict_parse(self, info):
        if not info[-1].isdigit():
            if info[-1].startswith("руб"):
                self.currency = "RUB"
            elif info[-1] == "$":
                self.currency = "USD"
            elif info[-1] == "€":
                self.currency = "EUR"
            else:
                self.currency = info[-1].upper()
            info = info[:-1]
        self.top_value = get_only_digits(info)

    def range_parse(self, info):
        # first is bottom
        self.bot_value = get_only_digits(info[0].split())
        # second is top
        self.strict_parse(info[1].split())

    def to_kzt(self, value):
        return value * round(rates.get_exchange_rate(self.currency, 'KZT'))


def get_only_digits(array):
    value = ""
    for a in array:
        if a.isdigit():
            value += a
    if value:
        return int(value)
    return 0


def vacancy_processing(v):
    link = v.find_element_by_tag_name("a")
    name = link.text
    for word in AVOID_WORDS:
        if word in name.lower():
            return
    salary_info = v.find_element_by_class_name("vacancy-serp-item__sidebar").text
    if not salary_info:
        return
    salary = Salary(salary_info)
    if salary.kzt < MINIMUM_SALARY:
        return
    print(f"Название:   {name}")
    print(f"Оклад:      {salary}")
    print(f"Ссылка:     {link.get_attribute('href')}\n")


def page_collector(url, current, stop):
    driver.get(url)
    table = driver.find_element_by_class_name("vacancy-serp")
    vacancies = table.find_elements_by_css_selector("div.vacancy-serp-item")

    for vacancy in vacancies[:-3]:
        try:
            vacancy_processing(vacancy)
        except exceptions.NoSuchElementException:
            pass
    try:
        next_page = driver.find_element_by_css_selector("a.bloko-button.HH-Pager-Controls-Next.HH-Pager-Control")
        url = next_page.get_attribute("href")
        if current > stop:
            return
        page_collector(url, current + 1, stop)
    except exceptions.NoSuchElementException:
        pass


if __name__ == "__main__":
    rates = Rates()
    options = webdriver.ChromeOptions()
    options.headless = True
    driver = webdriver.Chrome("chromedriver.exe", options=options)
    page_collector(START_PAGE, CURRENT_PAGE, STOP_PAGE)
    driver.quit()
