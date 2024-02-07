from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import apm
import rec1
import util
import sheets
city_links = sheets.get_city_links()
city = city_links[22]
city_name = city["abbreviation"]
full_url = city["full_url"]
provider = city["provider"]
username = city["user"]
password = city["password"]

driver = util.init_driver(headless=False)

driver.get(full_url)
rec1.login(driver, city_name, username, password)

util.is_on_page(driver, "locked")
util.is_on_page(driver, "incorrect")

driver.get(full_url)


WebDriverWait(driver, 5).until(EC.alert_is_present())

alert = driver.switch_to.alert

