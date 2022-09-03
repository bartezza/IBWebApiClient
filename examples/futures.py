
from pprint import pprint
from ibwebapiclient import IBWebApiClient, init_logging

# utility function to init colored logging
init_logging()

# connect to IB web API gateway
use_ibeam = False  # set to true if using ibeam
host = "localhost"
ibc = IBWebApiClient(use_ibeam=use_ibeam, host=host)

# search future contract with name "ES"
futures = ibc.search_futures(["ES"])
# select it
futures = futures["ES"]
# sort by expiration date
futs = sorted(futures, key=lambda x: x["expirationDate"])
# take the one expiring sooner
fut = futs[0]
pprint(fut)

# get contract info
es_conid = fut["conid"]
es_con = ibc.get_contract_info(es_conid)
pprint(es_con)
