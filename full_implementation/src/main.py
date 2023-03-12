import requests
import traceback

import lumen

from datetime import datetime, timezone, date, timedelta

def check_time(time_string):
    date_time  = datetime.strptime(time_string, "%Y-%m-%dT%H:%M:%SZ") # formatting the date time string
    now = datetime.now() # getting current datetime
    if date_time.replace(tzinfo=timezone.utc).timestamp() > now.replace(tzinfo=timezone.utc).timestamp(): # if the time string input is greater than the current time
        return(True)
    else:
        return(False)

def get_import_prices():
    import_prices = {}
    BASE_URL = "https://api.octopus.energy"
    PRODUCT_CODE = "AGILE-18-02-21" # This is the product code for ocotpus agile
    PRODUCT_CODE = "AGILE-FLEX-22-11-25"
    TARIFF_CODE = f"E-1R-{PRODUCT_CODE}-N" # The letter N specifies the south scotland region
    TARIFF_URL = f"{BASE_URL}/v1/products/{PRODUCT_CODE}/electricity-tariffs/{TARIFF_CODE}/standard-unit-rates/"
    r = requests.get(TARIFF_URL)
    octopus_import_prices = r.json()["results"]
    for time_period in octopus_import_prices:
        import_prices[time_period["valid_from"]] = time_period["value_inc_vat"] # getting all discrete prices for each half hour segment - this will include todays prices and the previous two days prices
    
    return(import_prices)

def get_export_prices():
    export_prices = {}
    BASE_URL = "https://api.octopus.energy"
    PRODUCT_CODE = "AGILE-OUTGOING-19-05-13"
    TARIFF_CODE = f"E-1R-{PRODUCT_CODE}-N" # The letter N specifies the south scotland region
    TARIFF_URL = f"{BASE_URL}/v1/products/{PRODUCT_CODE}/electricity-tariffs/{TARIFF_CODE}/standard-unit-rates/"
    r = requests.get(TARIFF_URL)
    octopus_export_prices = r.json()["results"]
    for time_period in octopus_export_prices:
        export_prices[time_period["valid_from"]] = time_period["value_inc_vat"] # getting all discrete prices for each half hour segment - this will include todays prices and the previous two days prices

    return(export_prices)

def get_15_min_list():
    date_times = []
    now = datetime.now() # getting the current date time
    starting_hour = now.hour * 100 # putting hours into millitary time 4 am = 400 hours, 4 pm = 1600 hours
    starting_minute = now.minute # getting the current run minute

    for i in range(0,2400,100): # for each hour in the next 24 hours
        temp_hour = starting_hour + i # increasingly itterating the hours 
        if starting_minute < 15: # if we are in the first quarter of the hour at initial run time
            last_full = temp_hour
            plus_quarter = temp_hour + 15 # the first time we want to schedule for will be quarter past the hour
            plus_half = temp_hour + 30 
            plus_three_quarter = temp_hour + 45

            if last_full > 2400:
                last_full = str(last_full - 2400)  + "_tomorrow"
            if plus_quarter > 2400: # if we have gone into tomorrow
                plus_quarter = str(plus_quarter - 2400) + "_tomorrow" # signify that we are in tomorrow by using
            if plus_half > 2400:
                plus_half = str(plus_half - 2400) + "_tomorrow"
            if plus_three_quarter > 2400:
                plus_three_quarter = str(plus_three_quarter - 2400)  + "_tomorrow"

            date_times.append(str(last_full))
            date_times.append(str(plus_quarter))
            date_times.append(str(plus_half))
            date_times.append(str(plus_three_quarter))

        if starting_minute >= 15 and starting_minute < 30: # if we are in the second quarter of the hour at run time
            last_quarter = temp_hour + 15
            plus_half = temp_hour + 30 # the first time we want to schedule the output for is at half past the hour
            plus_three_quarter = temp_hour + 45
            plus_full = temp_hour + 100

            if last_quarter > 2400:
                last_quarter = str(last_quarter - 2400) + "_tomorrow"
            if plus_half > 2400:
                plus_half = str(plus_half - 2400) + "_tomorrow"
            if plus_three_quarter > 2400:
                plus_three_quarter = str(plus_three_quarter - 2400)  + "_tomorrow"
            if plus_full > 2400:
                plus_full = str(plus_full - 2400)  + "_tomorrow"

            date_times.append(str(last_quarter))
            date_times.append(str(plus_half))
            date_times.append(str(plus_three_quarter))
            date_times.append(str(plus_full))

        if starting_minute >= 30 and starting_minute < 45: # if we are in the third quarter of the day
            last_half = temp_hour + 30
            plus_three_quarter = temp_hour + 45 # the first time we want to schedule the output for is at quarter to the next hour
            plus_full = temp_hour + 100
            plus_quarter = temp_hour + 100 + 15

            if plus_quarter > 2400:
                plus_quarter = str(plus_quarter - 2400) + "_tomorrow"
            if last_half > 2400:
                last_half = str(last_half - 2400) + "_tomorrow"
            if plus_three_quarter > 2400:
                plus_three_quarter = str(plus_three_quarter - 2400)  + "_tomorrow"
            if plus_full > 2400:
                plus_full = str(plus_full - 2400)  + "_tomorrow"

            date_times.append(str(last_half))
            date_times.append(str(plus_three_quarter))
            date_times.append(str(plus_full))
            date_times.append(str(plus_quarter))

        if starting_minute >= 45: # if we are in the final quarter of the hour at run time
            last_three_quarter = temp_hour + 45
            plus_full = temp_hour + 100 # the first time we want to schedule for is the start of the next hour
            plus_quarter = temp_hour + 100 + 15
            plus_half = temp_hour + 100 + 30

            if plus_quarter > 2400:
                plus_quarter = str(plus_quarter - 2400) + "_tomorrow"
            if plus_half > 2400:
                plus_half = str(plus_half - 2400) + "_tomorrow"
            if last_three_quarter > 2400:
                last_three_quarter = str(last_three_quarter - 2400)  + "_tomorrow"
            if plus_full > 2400:
                plus_full = str(plus_full - 2400)  + "_tomorrow"

            date_times.append(str(last_three_quarter))
            date_times.append(str(plus_full))
            date_times.append(str(plus_quarter))
            date_times.append(str(plus_half))
    return(date_times)

def get_price(date_time, import_prices, export_prices):
    now = datetime.now() # getting current datetime
    today = now.strftime("%d") # getting current day number

    month = now.strftime("%m") # getting current month
    year = now.strftime("%Y") # getting current year

    date_strings = []
    if "_tomorrow" in date_time: # if we need to find the price for tomorrow
        tomorrow = (date.today() + timedelta(days=1)).strftime("%d") # getting tomorrows zero padded day number

        if len(date_time) == 11: # we only have minutes "15_tomorrow" = 00:15:00 tomorrow
            hour = "00"
            minute = date_time[0:2]
            date_string = year + "-" + month + "-" + tomorrow + "T" + hour + ":" + minute + ":00" + "Z"

        if len(date_time) == 12: # we have hour and minute with no padding "115_tomorrow" = 01:15:00 tomorrow
            hour = "0" + date_time[0]
            minute = date_time[1:3]
            date_string = year + "-" + month + "-" + tomorrow + "T" + hour + ":" + minute + ":00" + "Z"
        
        if len(date_time) == 13: # we have zero padded and minutes "1115_tomorrow" = 11:15:00 tomorrow
            hour = date_time[0:2]
            minute = date_time[2:4]
            date_string = year + "-" + month + "-" + tomorrow + "T" + hour + ":" + minute + ":00" + "Z"

    else:
        if len(date_time) == 2: # we only have minutes
            hour = "00"
            minute = date_time[0:2]
            date_string = year + "-" + month + "-" + today + "T" + hour + ":" + minute + ":00" + "Z"

        if len(date_time) == 3: # we have hour and minute with no padding
            hour = "0" + date_time[0]
            minute = date_time[1:3]
            date_string = year + "-" + month + "-" + today + "T" + hour + ":" + minute + ":00" + "Z"
        
        if len(date_time) > 3: # we have zero padded and minutes
            hour = date_time[0:2]
            minute = date_time[2:4]
            date_string = year + "-" + month + "-" + today + "T" + hour + ":" + minute + ":00" + "Z"

    temp_date = date_string
    if ":15:" in date_string:
        temp_date = temp_date.replace(":15:", ":00:")
    if ":45:" in date_string:
        temp_date = temp_date.replace(":45:", ":30:")

    if "T24:00:00Z" in temp_date:
        temp_date = temp_date.replace("T24:00:00Z", "T00:00:00Z")
        date_string = date_string.replace("T24:00:00Z", "T00:00:00Z")

    try: # try to find the price 
        import_price = import_prices[temp_date]
        export_price = export_prices[temp_date]
    except: # if we cannot find the price for today lets get yesterdays price
        minutes_required = temp_date.split("T")[1]
        yesterday = (date.today() - timedelta(days=1)).strftime("%Y-%m-%dT")
        lookup = yesterday + minutes_required
        for key in import_prices.keys():
            if lookup == key:
                import_price = import_prices[key]
                export_price = export_prices[key]
    
    return(date_string, import_price, export_price)
    
try:
    a=1
    import_prices = get_import_prices()
    export_prices = get_export_prices()
    date_times = get_15_min_list()
    prices = []
    for date_time in date_times:
        time, import_price, export_price = get_price(date_time, import_prices, export_prices)
        temp = {"time": time,
                "import_price": import_price,
                "export_price": export_price}
        prices.append(temp)

    lumen.save({"prices":prices})
except Exception as e:
    lumen.save_exception(traceback.format_exc())
