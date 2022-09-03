
from ibwebapiclient import IBWebApiClient, init_logging

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

# get pandas dataframe with market history
period = "30d"
bar = "5min"
exchange = None
outside_rth = True
df = ibc.get_market_history_df(conid=conid, period=period, bar=bar,
                               exchange=exchange, outside_rth=outside_rth)
print(df.head())
