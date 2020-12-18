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
            self.kzt = self.coverter(self.top_value)
        else:
            self.range_parse(info)
            self.kzt = self.coverter(self.bot_value)

    def __str__(self):
        if not self.bot_value:
            output = f"{self.top_value} {self.currency}"
            if self.currency != "KZT":
                output += f" ({self.kzt} в KZT)"
        else:
            output = f"{self.bot_value} - {self.top_value} {self.currency}"
            if self.currency != "KZT":
                output += f" ({self.kzt} - {self.coverter(self.top_value)} в KZT)"
        return output

    def strict_parse(self, info):
        if info[-1].isalpha():
            # TODO currency. example: kzt and KZT to KZT
            self.currency = info[-1]
            info = info[:-1]
        else:
            self.currency = "KZT"
        self.top_value = get_only_digits(info)

    def range_parse(self, info):
        # first is bottom
        self.bot_value = get_only_digits(info[0].split())
        # second is top
        self.strict_parse(info[1].split())

    def coverter(self, value):
        return value


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
        print(Salary(salary))
        print()
    except exceptions.NoSuchElementException:
        pass
driver.quit()
