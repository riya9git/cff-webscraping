import apm
import util
import sheets
city_links = sheets.get_city_links()
city = city_links[1]
city_name = city["abbreviation"]
login_url = city["full_url"]
provider = city["provider"]
rosters_url = f"{login_url}/roster"

driver = util.init_driver(headless=False)

driver.get(rosters_url)
apm.login(driver, city["full_url"])

util.is_on_page(driver, "locked")
util.is_on_page(driver, "incorrect")

driver.get(rosters_url)

