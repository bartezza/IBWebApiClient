
from pprint import pprint
import time
from ibwebapiclient import IBWebApiClient, init_logging, build_bracket_order, OrderSide

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

# build bracket order
price = 50.0
quantity = 1
price_profit = 90.0
price_loss = 20.0
orders = build_bracket_order(conid=conid, side=OrderSide.BUY, price=price, quantity=quantity,
                             price_profit=price_profit, price_loss=price_loss)

# submit order
ret = ibc.submit_order(orders=orders)
pprint(ret)

# wait a bit, to get order registered
time.sleep(2)
# print orders
orders = ibc.get_orders()
print(f"{len(orders)} orders:")
for order in orders:
    print(f" - {order.ticker} {order.orderDesc}, {order.lastExecutionTime}, {order.status}")
