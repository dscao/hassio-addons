LOGIN_URL = "https://www.95598.cn/osgweb/login"
ELECTRIC_USAGE_URL = "https://www.95598.cn/osgweb/electricityCharge"
BALANCE_URL = "https://www.95598.cn/osgweb/userAcc"

SUPERVISOR_URL = "http://supervisor/core"
API_PATH = "/api/states/"

BALANCE_SENSOR_NAME = "sensor.electricity_charge_balance"
DAILY_USAGE_SENSOR_NAME = "sensor.last_electricity_usage"
YEARLY_USAGE_SENSOR_NAME = "sensor.yearly_electricity_usage"
YEARLY_CHARGE_SENESOR_NAME = "sensor.yearly_electricity_charge"
BALANCE_UNIT = "CNY"
USAGE_UNIT = "kWh"

JOB_INTERVAL_HOURS = 8  # Please DO NOT make it too frequently.
DRIVER_IMPLICITY_WAIT_TIME = 20
RETRY_TIMES_LIMIT = 5
LOGIN_EXPECTED_TIME = 10
RETRY_WAIT_TIME_OFFSET_UNIT = 10
