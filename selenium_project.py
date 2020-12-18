from selenium.common import exceptions
from selenium import webdriver


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
            salary = "No information"
        print(f"Название:\t{name}")
        print(f"Оклад:\t{salary}")
        print()
    except exceptions.NoSuchElementException:
        pass
driver.quit()
