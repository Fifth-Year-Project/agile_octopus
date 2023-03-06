import requests
import traceback

import full_implementation.src.lumen as lumen

from datetime import datetime, timezone

def check_time(time_string):
    date_time  = datetime.strptime(time_string, "%Y-%m-%dT%H:%M:%SZ")
    now = datetime.now()
    if date_time.replace(tzinfo=timezone.utc).timestamp() > now.replace(tzinfo=timezone.utc).timestamp():
        return(True)
    else:
        return(False)
    
def extrapolate_import_prices(len(export_prices), historic_export_prices):
    while export_prices < 24: # if true we will have to extrapolate data
        
        # Get yesterdays data
        # Append missing values



try:
    #AGILE-OUTGOING-19-05-13
    #
    BASE_URL = "https://api.octopus.energy"
    PRODUCT_CODE = "AGILE-18-02-21" # This is the product code for ocotpus agile
    PRODUCT_CODE = "AGILE-FLEX-22-11-25"
    TARIFF_CODE = f"E-1R-{PRODUCT_CODE}-N" # The letter N specifies the south scotland region
    TARIFF_URL = f"{BASE_URL}/v1/products/{PRODUCT_CODE}/electricity-tariffs/{TARIFF_CODE}/standard-unit-rates/"
    r = requests.get(TARIFF_URL)
    octopus_import_prices = r.json()["results"]
    import_prices = {}
    historic_import_prices = {}
    for time_period in octopus_import_prices:
        if check_time(time_period["valid_from"]):
            import_prices[time_period["valid_from"]] = time_period["value_inc_vat"]
        else:
            historic_import_prices[time_period["valid_from"]] = time_period["value_inc_vat"]


    PRODUCT_CODE = "AGILE-OUTGOING-19-05-13"
    TARIFF_CODE = f"E-1R-{PRODUCT_CODE}-N" # The letter N specifies the south scotland region
    TARIFF_URL = f"{BASE_URL}/v1/products/{PRODUCT_CODE}/electricity-tariffs/{TARIFF_CODE}/standard-unit-rates/"
    r = requests.get(TARIFF_URL)
    octopus_export_prices = r.json()["results"]
    export_prices = {}
    historic_export_prices = {}
    for time_period in octopus_export_prices:
        if check_time(time_period["valid_from"]):
            export_prices[time_period["valid_from"]] = time_period["value_inc_vat"]
        else:
            historic_export_prices[time_period["valid_from"]] = time_period["value_inc_vat"]
    
    results = {"import_prices": import_prices, "export_prices" : export_prices}
    lumen.save(results)
except:
    lumen.save_exception(traceback.format_exc())