from data_fetcher import DataFetcher
from sensor_updator import SensorUpdator, SensorentityUpdator
import sys
import logging
import logging.config
import traceback
from const import *
import schedule
import time, datetime
import re

def main():
    args = argvs_parsor()
    logger_init(args["log_level"])
    logging.info("Service start!")

    fetcher = DataFetcher(args["phone_number"], args["password"])
    updator = SensorUpdator(args["hass_url"], args["hass_token"])
    entityupdator = SensorentityUpdator(args["hass_url"], args["hass_token"])
    schedule.every(JOB_INTERVAL_HOURS).hours.do(run_task, fetcher, updator)
    run_task(fetcher, entityupdator)
    while True:
        schedule.run_pending()
        time.sleep(1)

def run_task(data_fetcher: DataFetcher, sensorentity_updator: SensorentityUpdator):
    try:
        balance, balance_list_pay, balance_list_need_pay, last_daily_usage_list, yearly_charge_list, yearly_usage_list, thismonth_usage_list, last_date_list = data_fetcher.fetch()
        sensorentity_updator.update("sensor.electricity_95598", balance, {"unit_of_measurement": "CNY", "is_pay": balance_list_pay, "need_pay": balance_list_need_pay, "last_electricity_usage": last_daily_usage_list, "yearly_electricity_usage": yearly_usage_list, "yearly_electricity_charge": yearly_charge_list, "thismonth_electricity_usage": thismonth_usage_list, "last_date":last_date_list, "update_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")},)
        logging.info("state-refresh task run successfully!")
    except Exception as e:
        logging.error(f"state-refresh task failed, reason is {e}")
        traceback.print_exc()

def run_task(data_fetcher: DataFetcher, sensorentity_updator: SensorentityUpdator):
    try:
        user_id_list, balance_list, balance_list_pay, balance_list_need_pay, last_daily_usage_list, yearly_charge_list, yearly_usage_list, thismonth_usage_list, last_date_list = data_fetcher.fetch()
        for i in range(0, len(user_id_list)):
            profix = f"_{user_id_list[i]}" if len(user_id_list) > 1 else ""
            sensorentity_updator.update("sensor.electricity_95598" + profix,  balance_list[i], {"unit_of_measurement": "CNY", "is_pay": balance_list_pay[i], "need_pay": balance_list_need_pay[i], "last_electricity_usage": last_daily_usage_list[i], "yearly_electricity_usage": yearly_usage_list[i], "yearly_electricity_charge": yearly_charge_list[i], "thismonth_electricity_usage": thismonth_usage_list[i],"last_date":last_date_list[i], "update_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")},)

        logging.info("state-refresh task run successfully!")
    except Exception as e:
        logging.error(f"state-refresh task failed, reason is {e}")
        traceback.print_exc()
        
def argvs_parsor():
    args = {
    "phone_number": "",
    "password":"",
    "log_level":"INFO",
    "hass_url":"",
    "hass_token":""
    }
    pattern = r"--(.*)=(.*)"
    
    for arg in sys.argv[1:]:
        match_result = re.match(pattern,arg)
        if(None != match_result):
            vars = match_result.groups()
            key = vars[0].lower()
            if(len(vars) == 2 and None != args[key]):
                args[key] = vars[1]

    for value in args.values():
        if(len(value) == 0):
            raise Exception("error occured when parsing args. Have you set all required environment variable?")
    return args

def logger_init(level: str):
    logger = logging.getLogger()
    logger.setLevel(level)
    logging.getLogger("urllib3").setLevel(logging.CRITICAL)
    format = logging.Formatter("%(asctime)s  [%(levelname)-8s] ---- %(message)s","%Y-%m-%d %H:%M:%S")
    sh = logging.StreamHandler(stream=sys.stdout) 
    sh.setFormatter(format)
    logger.addHandler(sh)


if(__name__ == "__main__"):
    main()
