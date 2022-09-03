
import requests
from time import sleep
from ibwebapiclient import IBWebApiClient, init_logging

# utility function to init colored logging
init_logging()

# connect to IB web API gateway
use_ibeam = False  # set to true if using ibeam
host = "localhost"
ibc = IBWebApiClient(use_ibeam=use_ibeam, host=host)

# loop forever until interrupted
while True:
    try:
        # ping IB gateway
        ibc.ping_gateway()
    except requests.exceptions.HTTPError as exc:
        # log error but do not stop the loop
        ibc._log.error(str(exc))
    # wait before next ping
    sleep(1)
