
# IBWebApiClient

Python client for simplifying the interaction with Interactive Brokers Client
Portal Web API.

Installing, running and authenticating through the IB gateway is necessary,
before using this library to talk to it.
A good solution is to use [ibeam](https://github.com/Voyz/ibeam) to automatically
handle management of the gateway, including authentication.

For usage examples see folder `examples`.

## Installation

Once this repository has been cloned locally, you can do a local installation:

```console
pip install .
```

or, if you plan to modify the source code, you can install it in development
mode:

```console
pip install -e .
```

All dependencies are listed in the `setup.py` file and will be installed
automatically.

## Example usage

For further examples see folder `examples`.

```python
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
df = ibc.get_market_history_df(conid=conid, period=period, bar=bar,
                               exchange=exchange, outside_rth=outside_rth)
print("\nMarket history:")
print(df.head())
```
## Example with realtime market data

For realtime market data, websockets are used to register the requested market
feeds with the IB gateway. Then, data is retrieved by polling the REST endpoint.

```python
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
```

## Similar libraries

 - https://github.com/areed1192/interactive-broker-python-api
 - https://github.com/areed1192/interactive-brokers-api

## References

 - [Official API documentation](https://www.interactivebrokers.com/api/doc.html)
