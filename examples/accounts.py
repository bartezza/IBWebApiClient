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
print("\nPortfolio accounts:")
pprint(accs)

# get positions
poss = ibc.get_positions()
print("\nPositions:")
pprint(poss)
