
from pprint import pprint
from datetime import datetime
from ibwebapiclient import IBWebApiClient, init_logging

# utility function to init colored logging
init_logging()

# connect to IB web API gateway
use_ibeam = False  # set to true if using ibeam
host = "localhost"
ibc = IBWebApiClient(use_ibeam=use_ibeam, host=host)

# search SPX index
sec = ibc.search_security(symbol="SPX", sec_type="IDX")
# use first result
spx = sec[0]
conid = spx["conid"]
# get first valid expiration date for options
expirations = spx["opt"].split(";")
expiration = expirations[0]

print(f"{conid} - {spx['companyHeader']} - expiration = {expiration}")

# get option info for all strikes
opts = ibc.get_options_info(conid=conid, expiration=expiration, strike=None)
pprint(opts)

# get option strikes at expiration
strikes = ibc.get_option_strikes(conid=conid, expiration=expiration)
pprint(strikes)

# get last prices from market data
data = ibc.get_market_history(conid=conid, period="2d", bar="1d", outside_rth=False)
dt = datetime.fromtimestamp(data.data[0]["t"] / 1000)
last = data.data[0]["c"]
print(f"dt = {dt}, last = {last}")

# get option closest strike to last price
strike_idx, strike = ibc.get_closest_strike(strikes, last)
print(f"strike = {strike}")

# get option info for a specific strike
opts = ibc.get_options_info(conid=conid, expiration=expiration, strike=strike)
pprint(opts)

# get full option chain
oc = ibc.get_option_chain(conid=conid, expiration=expiration)
print(f"calls = {len(oc.call)}, puts = {len(oc.put)}")
