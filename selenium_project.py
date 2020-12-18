from selenium.common import exceptions
from selenium import webdriver


def get_only_digits(array):
    value = ""
    for a in array:
        if a.isdigit():
            value += a
    if value:
        return int(value)
    return 0


class Salary:
    top_value = 0
    bot_value = 0
    currency = ""
    kzt = 0

    def __init__(self, info):
        info = info.split("-")
        if len(info) == 1:
            self.strict_parse(info[0].split())
        else:
            self.range_parse(info)

    def strict_parse(self, info):
        if info[-1].isalpha():
            # TODO currency. example: kzt and KZT to KZT
            self.currency = info[-1]
            info = info[:-1]
        else:
            self.currency = "KZT"
        value = get_only_digits(info)
        self.top_value = int(value)

    def range_parse(self, info):
        # first is bottom
        value = get_only_digits(info[0].split())
        self.bot_value = int(value)
        # second is top
        self.strict_parse(info[1].split())


url = "https://hh.kz/search/vacancy?clusters=true&enable_snippets=true&text=python&L_save_area=true&area=159&from" \
      "=cluster_area&showClusters=true "
options = webdriver.ChromeOptions()
options.headless = True
driver = webdriver.Chrome("chromedriver.exe", options=options)

driver.get(url)
table = driver.find_element_by_class_name("vacancy-serp")
vacancies = table.find_elements_by_xpath("//*[@class='vacancy-serp-item__row vacancy-serp-item__row_header']")

for vacancy in vacancies:
    try:
        name = vacancy.find_element_by_tag_name("a").text
        if "преподаватель" in name.lower():
            continue
        salary = vacancy.find_element_by_class_name("vacancy-serp-item__sidebar").text
        if not salary:
            # salary = "No information"
            continue
        print(f"Название:\t{name}")
        print(f"Оклад:\t{salary}")
        print()
    except exceptions.NoSuchElementException:
        pass
driver.quit()
