
from pprint import pprint
import time
from ibwebapiclient import IBWebApiClient, MarketDataFields, init_logging

# utility function to init colored logging
init_logging()

# connect to IB web API gateway
use_ibeam = False  # set to true if using ibeam
host = "localhost"
ibc = IBWebApiClient(use_ibeam=use_ibeam, host=host)

# search securities with this symbol
sec = ibc.search_security("AAPL", "STK")
# take first one and get contract
conid = sec[0]["conid"]
con_info = ibc.get_contract_info(conid)
print(f"{con_info.con_id} - {con_info.symbol} - {con_info.company_name}")

# unsubscribe from all market data feeds
# ibc.unsubscribe_all_market_data()

# get default market data fields for stocks
fields = ibc.get_market_data_fields(def_fields="STK")
# add some more fields
fields += [
    MarketDataFields.EMAOneHundred.value,
    MarketDataFields.EMATwoHundred.value
]
# subscribe to market data feed, with the given fields
ibc.subscribe_market_data(conid=conid, fields=fields)

# poll loop
while True:
    # get snapshot of market data for the given security
    ret = ibc.get_market_data_snapshot(conid=conid)
    print("")
    pprint(ret)
    # wait a bit
    time.sleep(2)
