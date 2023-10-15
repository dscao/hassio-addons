import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import ddddocr
import time
import logging
import traceback
import subprocess
import re
import sys
from const import *


class DataFetcher:

    def __init__(self, username: str, password: str):

        self._username = username
        self._password = password
        self._ocr = ddddocr.DdddOcr(show_ad = False)
        self._chromium_version = self._get_chromium_version()

    
    def fetch(self):
        '''the entry, only retry logic here '''
        for retry_times in range(1, RETRY_TIMES_LIMIT + 1):
            try:
                return self._fetch()
            except Exception as e:
                if(retry_times == RETRY_TIMES_LIMIT):
                    raise e
                traceback.print_exc()
                logging.error(f"Webdriver quit abnormly, reason: {e}. {RETRY_TIMES_LIMIT - retry_times} retry times left.")
                wait_time = retry_times * RETRY_WAIT_TIME_OFFSET_UNIT
                time.sleep(wait_time)
                
            
    
    def _fetch(self):
        '''main logic here'''

        driver = self._get_webdriver()
        logging.info("Webdriver initialized.")
        try:
            self._login(driver)
            logging.info(f"Login successfully on {LOGIN_URL}" )

            user_id_list = self._get_user_ids(driver)
            logging.info(f"get all user id: {user_id_list}")

            balance_list, balance_list_pay, balance_list_need_pay = self._get_electric_balances(driver, user_id_list)
            ### get data except electricity charge balance
            last_daily_usage_list, yearly_charge_list, yearly_usage_list, thismonth_usage_list, last_date_list = self._get_other_data(driver, user_id_list)

            driver.quit()

            logging.info("Webdriver quit after fetching data successfully.")

            return user_id_list, balance_list, balance_list_pay, balance_list_need_pay, last_daily_usage_list, yearly_charge_list, yearly_usage_list, thismonth_usage_list

        finally:
                driver.quit()

    def _get_webdriver(self):
        chrome_options = Options()
        chrome_options.add_argument('--incognito')
        chrome_options.add_argument('--window-size=4000,1600')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-dev-shm-usage')
        driver = uc.Chrome(driver_executable_path = "/usr/bin/chromedriver" ,options = chrome_options, version_main = self._chromium_version)
        driver.implicitly_wait(DRIVER_IMPLICITY_WAIT_TIME)
        return driver

    def _login(self, driver):

        driver.get(LOGIN_URL)

        # swtich to username-password login page
        driver.find_element(By.CLASS_NAME,"user").click()

        # input username and password
        input_elements = driver.find_elements(By.CLASS_NAME,"el-input__inner")
        input_elements[0].send_keys(self._username)
        input_elements[1].send_keys(self._password)
        
        captcha_element = driver.find_element(By.CLASS_NAME,"code-mask")
        
        # sometimes ddddOCR may fail, so add retry logic)
        for retry_times in range(1, RETRY_TIMES_LIMIT + 1):

            img_src = captcha_element.find_element(By.TAG_NAME,"img").get_attribute("src")
            img_base64 = img_src.replace("data:image/jpg;base64,","")
            orc_result = str(self._ocr.classification(ddddocr.base64_to_image(img_base64)))

            if(not self._is_captcha_legal(orc_result)):
                logging.debug(f"The captcha is illegal, which is caused by ddddocr, {RETRY_TIMES_LIMIT - retry_times} retry times left.")
                WebDriverWait(driver, DRIVER_IMPLICITY_WAIT_TIME).until(EC.element_to_be_clickable(captcha_element))
                driver.execute_script("arguments[0].click();", captcha_element)
                time.sleep(2)
                continue

            input_elements[2].send_keys(orc_result)
            
            # click login button
            self._click_button(driver, By.CLASS_NAME, "el-button.el-button--primary")
            try:
                return WebDriverWait(driver,LOGIN_EXPECTED_TIME).until(EC.url_changes(LOGIN_URL))
            except:
                logging.debug(f"Login failed, maybe caused by invalid captcha, {RETRY_TIMES_LIMIT - retry_times} retry times left.")

        raise Exception("Login failed, maybe caused by 1.incorrect phone_number and password, please double check. or 2. network, please mondify LOGIN_EXPECTED_TIME in const.py and rebuild.")

    def _get_electric_balances(self, driver, user_id_list):

        balance_list = []
        balance_list_pay = []
        balance_list_need_pay = []

        # switch to electricity charge balance page
        driver.get(BALANCE_URL)

        # get electricity charge balance for each user id
        for i in range(1, len(user_id_list) + 1):
            balance = self._get_eletric_balance(driver)
            balance_pay = self._get_eletric_balance_pay(driver)
            if (balance_pay == "当期已结清" or balance_pay == "预计可用天数"):
                balance_need_pay = 0
            else:
                balance_need_pay = balance
            logging.info(f"Get electricity charge balance for {user_id_list[i-1]} successfully, balance is {balance} CNY, is_pay {balance_pay}, need_pay is {balance_need_pay} CNY.")
            
            balance_list.append(balance)
            balance_list_pay.append(balance_pay)
            balance_list_need_pay.append(balance_need_pay)
            
            # swtich to next userid
            if(i != len(user_id_list)):
                self._click_button(driver, By.CLASS_NAME, "el-input.el-input--suffix")
                self._click_button(driver, By.XPATH, f"//ul[@class='el-scrollbar__view el-select-dropdown__list']/li[{i + 1}]")

        return balance_list, balance_list_pay, balance_list_need_pay
    
    def _get_other_data(self, driver, user_id_list):

        last_daily_usage_list =[]
        yearly_usage_list = []
        yearly_charge_list = []
        thismonth_usage_list = []
        last_date_list = []

        # swithc to electricity usage page
        driver.get(ELECTRIC_USAGE_URL)

        # get data for each user id
        for i in range(1, len(user_id_list) + 1):

            yearly_usage, yearly_charge, thismonth_usage, last_date = self._get_yearly_data(driver)
            logging.info(f"Get year power consumption for {user_id_list[i-1]} successfully, yearly_usage is {yearly_usage} kwh, yealrly charge is {yearly_charge} CNY, thismonth_usage is {thismonth_usage} kwh, last_date is {last_date}")

            last_daily_usage = self._get_yesterday_usage(driver)
            logging.info(f"Get daily power consumption for {user_id_list[i-1]} successfully, usage is {last_daily_usage} kwh.")

            last_daily_usage_list.append(last_daily_usage)
            yearly_charge_list.append(yearly_charge)
            yearly_usage_list.append(yearly_usage)
            thismonth_usage_list.append(thismonth_usage)
            last_date_list.append(last_date)

            # switch to next user id
            if(i != len(user_id_list)):
                self._click_button(driver, By.CLASS_NAME, "el-input.el-input--suffix")
                self._click_button(driver, By.XPATH, f"//body/div[@class='el-select-dropdown el-popper']//ul[@class='el-scrollbar__view el-select-dropdown__list']/li[{i + 1}]")
            
        return last_daily_usage_list, yearly_charge_list, yearly_usage_list, thismonth_usage_list, last_date_list

    def _get_user_ids(self, driver):

        # click roll down button for user id
        self._click_button(driver, By.XPATH, "//div[@class='el-dropdown']/span")
        # wait for roll down menu displayed
        target = driver.find_element(By.CLASS_NAME, "el-dropdown-menu.el-popper").find_element(By.TAG_NAME, "li")
        WebDriverWait(driver, DRIVER_IMPLICITY_WAIT_TIME).until(EC.visibility_of(target))
        WebDriverWait(driver, DRIVER_IMPLICITY_WAIT_TIME).until(EC.text_to_be_present_in_element((By.XPATH, "//ul[@class='el-dropdown-menu el-popper']/li"), ":"))

        # get user id one by one
        userid_elements = driver.find_element(By.CLASS_NAME, "el-dropdown-menu.el-popper").find_elements(By.TAG_NAME, "li")
        userid_list = []
        for element in userid_elements:
            userid_list.append(re.findall("[0-9]+", element.text)[-1])
        return userid_list

    def _get_eletric_balance(self, driver):
        balance = driver.find_element(By.CLASS_NAME,"num").text
        return float(balance)
        
    def _get_eletric_balance_pay(self, driver):
        balance_pay = driver.find_elements(By.CLASS_NAME,"amttxt")[1].text
        return str(balance_pay)
    
    def _get_yearly_data(self, driver):

        self._click_button(driver, By.XPATH, "//div[@class='el-tabs__nav is-top']/div[@id='tab-first']")

        # wait for data displayed
        target = driver.find_elements(By.CLASS_NAME, "total")
        if target:
            # WebDriverWait(driver, DRIVER_IMPLICITY_WAIT_TIME).until(EC.visibility_of(target))
        
            # get data
            yearly_usage = driver.find_element(By.XPATH, "//ul[@class='total']/li[1]/span").text
            yearly_charge = driver.find_element(By.XPATH, "//ul[@class='total']/li[2]/span").text
        else:
            yearly_usage = 0
            yearly_charge = 0
        
        
        
        self._click_button(driver, By.XPATH, "//div[@class='el-tabs__nav is-top']/div[@id='tab-second']")
        
        # wait for data displayed
        target = driver.find_element(By.XPATH, "//div[@class='el-radio-group radio']")
        WebDriverWait(driver, DRIVER_IMPLICITY_WAIT_TIME).until(EC.visibility_of(target))
        
        self._click_button(driver, By.XPATH, "//span[text()='近30天']")
        
        # wait for data displayed
        target = driver.find_element(By.CLASS_NAME, "numerical")
        WebDriverWait(driver, DRIVER_IMPLICITY_WAIT_TIME).until(EC.visibility_of(target))
        
        # get data
        thismonth_usage = 0
        electricity_date_list = driver.find_elements(By.XPATH, "//div[@class='el-table__body-wrapper is-scrolling-none']/table/tbody/tr/td[1]/div")
        electricity_value_list = driver.find_elements(By.XPATH, "//div[@class='el-table__body-wrapper is-scrolling-none']/table/tbody/tr/td[2]/div")
        
        # logging.info(f"electricity_last_date： {electricity_date_list[0].text} ")
        
        last_date = electricity_date_list[0].text
        
        thismonth = last_date.split("-")[1]
        
        logging.info(f"thismonth： {thismonth} ")
        
        for m in range(0, len(electricity_date_list)):
            if electricity_date_list[m].text.split("-")[1] == thismonth:
                thismonth_usage += float(electricity_value_list[m].text)
                
        return yearly_usage, yearly_charge, round(thismonth_usage,2), last_date

        

    def _get_yesterday_usage(self, driver):
        self._click_button(driver, By.XPATH,"//div[@class='el-tabs__nav is-top']/div[@id='tab-second']")
        # wait for data displayed
        usage_element = driver.find_element(By.XPATH,"//div[@class='el-tab-pane dayd']//div[@class='el-table__body-wrapper is-scrolling-none']/table/tbody/tr[1]/td[2]/div")
        WebDriverWait(driver, DRIVER_IMPLICITY_WAIT_TIME). until(EC.visibility_of(usage_element))
        return(float(usage_element.text))

    @staticmethod
    def _click_button(driver, button_search_type, button_search_key):
        '''wrapped click function, click only when the element is clickable'''
        click_element = driver.find_element(button_search_type, button_search_key)
        WebDriverWait(driver, DRIVER_IMPLICITY_WAIT_TIME).until(EC.element_to_be_clickable(click_element))
        driver.execute_script("arguments[0].click();", click_element)

    @staticmethod
    def _is_captcha_legal(captcha):
        ''' check the ddddocr result, justify whether it's legal'''
        if(len(captcha) != 4): 
            return False
        for s in captcha:
            if(not s.isalpha() and not s.isdigit()):
                return False
        return True
    
    @staticmethod
    def _get_chromium_version():
        result = str(subprocess.check_output(["chromium", "--product-version"]))
        return re.findall(r"(\d*)\.",result)[0]

if(__name__ == "__main__"):
    '''You can test it in the docker container. Replace the following params and use 'python3 data_fetcher.py' '''

    logger = logging.getLogger()
    logger.setLevel("INFO")
    logging.getLogger("urllib3").setLevel(logging.CRITICAL)
    format = logging.Formatter("%(asctime)s  [%(levelname)-8s] ---- %(message)s","%Y-%m-%d %H:%M:%S")
    sh = logging.StreamHandler(stream=sys.stdout) 
    sh.setFormatter(format)
    logger.addHandler(sh)
    
    fetcher = DataFetcher("CHNAGE_ME_PHONE_NUMBER","CHANGE_ME_PASSWORD")
    print(fetcher.fetch())
