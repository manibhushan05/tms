from time import sleepfrom restapi.seleniumautomation.comman_setup import get_browser, login#sample dataminimum_driver_data_for_create = {    "name": "Mr.X",    "phone": "7878787878"}full_driver_data_for_create = {    "name": "some_driver",    "phone": "9898989898",    "alt_phone": "9898989899",    "alt_phone2": "9898989800",    "dl_number": "2345343534",    "route": "delhiToJaipur"}minimum_driver_data_for_update = {    "id": "5580",    "name": "Mr.Jhonson",    "phone": "7000008098"}full_driver_data_for_update = {    "id": "5589",    "name": "updated_driver",    "phone": "9898980000",    "alt_phone": "8898989899",    "alt_phone2": "9898989800",    "dl_number": "987343233",    "route": "BhopalToJaipur"}def create_driver(data):    browser = get_browser()    login(browser)    # finding registration tab    registrationTab = browser.find_element_by_css_selector("i[class='fa fa-registered']")    sleep(1)    # click registration tab    registrationTab.click()    sleep(2)    #find driver tab and click    driverpageElem = browser.find_element_by_css_selector("a[data-url='/page/register-sme-page/']")    browser.execute_script("arguments[0].scrollIntoView();", driverpageElem)    sleep(5)    driverpageElem.click()    sleep(5)    #finding fields for creating driver    driverName = browser.find_element_by_css_selector("input[name='name']")    driverPhone = browser.find_element_by_css_selector("input[name='phone']")    driverAltPhone1 = browser.find_element_by_css_selector("input[name='alt_phone']")    driverAltPhone2 = browser.find_element_by_css_selector("input[name='alt_phone2']")    dlNumber = browser.find_element_by_css_selector("input[name='driving_licence_number']")    route = browser.find_element_by_css_selector("input[name='route']")    registerDriverButton = browser.find_element_by_id("btn-register-driver")    #filling all fields    if "name" in data:        driverName.send_keys(data["name"])        sleep(2)    if "phone" in data:        driverPhone.send_keys(data["phone"])        sleep(2)    if "alt_phone" in data:        driverAltPhone1.send_keys(data["alt_phone"])        sleep(2)    if "alt_phone2" in data:        driverAltPhone2.send_keys(data["alt_phone2"])        sleep(2)    if "dl_number" in data:        dlNumber.send_keys(data["dl_number"])        sleep(2)    if "route" in data:        route.send_keys(data["route"])        sleep(2)    #click on register_driver button    registerDriverButton.click()    sleep(10)    browser.quit()def update_driver(data):    browser = get_browser()    # going to all driver list page    login(browser)    sleep(5)    UpdateElem = browser.find_element_by_css_selector("i[class='fa fa-refresh']")    browser.execute_script("arguments[0].scrollIntoView();", UpdateElem)    sleep(5)    UpdateElem.click()    sleep(1)    driverUpdatePage = browser.find_element_by_css_selector("a[data-url='/page/driver-list-page/']")    browser.execute_script("arguments[0].scrollIntoView();", driverUpdatePage)    sleep(5)    driverUpdatePage.click()    sleep(5)    # opening a particular driver page to update details    uniqueDriver = browser.find_element_by_css_selector("a[data-url='/api/driver-driver-retrieve/{}/']".format(data["id"]))    sleep(2)    uniqueDriver.click()    sleep(5)    #updating driver details    nameField = browser.find_element_by_css_selector("input[name='name']")    phoneField = browser.find_element_by_css_selector("input[name='phone']")    altphone1Field = browser.find_element_by_css_selector("input[name='alt_phone']")    altphone2Field = browser.find_element_by_css_selector("input[name='alt_phone2']")    dlnumberField = browser.find_element_by_css_selector("input[name='driving_licence_number']")    routeField = browser.find_element_by_css_selector("input[name='route']")    updateButton = browser.find_element_by_css_selector("button[id='btn-update-driver']")    sleep(2)    if "name" in data:        nameField.send_keys(data["name"])        sleep(2)    if "phone" in data:        phoneField.send_keys(data["phone"])        sleep(2)    if "alt_phone" in data:        altphone1Field.send_keys(data["alt_phone"])        sleep(2)    if "alt_phone2" in data:        altphone2Field.send_keys(data["alt_phone2"])        sleep(2)    if "dl_number" in data:        dlnumberField.send_keys(data["dl_number"])        sleep(2)    if "route" in data:        routeField.send_keys(data["route"])        sleep(2)    #click update button    updateButton.click()    sleep(10)    browser.quit()