from pprint import pprint

from ibwebapiclient import IBWebApiClient, init_logging

# utility function to init colored logging
init_logging()

# connect to IB web API gateway
use_ibeam = False  # set to true if using ibeam
host = "localhost"
ibc = IBWebApiClient(use_ibeam=use_ibeam, host=host)

# get portfolio accounts
accs = ibc.get_portfolio_accounts()
print("\nAccounts:")
pprint(accs)

# get open positions
poss = ibc.get_positions()
print("\nPositions:")
pprint(poss)

# get orders
orders = ibc.get_orders()
print("\nOrders:")
pprint(orders)

# get trades
trades = ibc.get_trades()
print("\nTrades:")
pprint(trades)

# look for futures named "ES"
futures = ibc.search_futures(["ES"])
# sort them by expiration date
futures = futures["ES"]
futures = sorted(futures, key=lambda x: x["expirationDate"])
# take the one expiring sooner
es_fut = futures[0]
print("\nES:")
pprint(es_fut)

# retrieve contract info
conid = es_fut["conid"]
con_info = ibc.get_contract_info(conid)
print("\nContract info:")
pprint(con_info)

# get pandas dataframe with market history
period = "30d"
bar = "5min"
exchange = None
outside_rth = True
df = ibc.get_market_history_df(conid=conid,
                               period=period,
                               bar=bar,
                               exchange=exchange,
                               outside_rth=outside_rth)
print("\nMarket history:")
print(df.head())
