import socket
import json
import logging
from typing import Optional, List, Union, Tuple
import requests
from requests.exceptions import ConnectTimeout
from urllib3.exceptions import InsecureRequestWarning
import warnings
import pandas as pd
from datetime import datetime
from websocket import create_connection
import ssl
from .models import (MarketDataFields, ContractInfo, OptionInfo, OptionStrikes, MarketHistory, OptionChain,
                     market_data_fields_map, GatewayStatus, Order)

# ignore SSL verification warnings since we need to connect to the IB gateway,
# which is using a self-signed certificate
warnings.simplefilter('ignore', InsecureRequestWarning)


def expiration_to_month(datestr: str) -> str:
    """Extract month from expiration.

    Example: 20220822 => AUG22."""
    dt = datetime(year=int(datestr[0:4]), month=int(datestr[4:6]), day=int(datestr[6:8]))
    month = dt.strftime("%b%y").upper()
    return month


class IBWebApiClient:
    _log: logging.Logger = logging.getLogger("IBWebApiClient")
    _api_url: str = "https://{host}:5000/v1/api/"
    _ws_url: str = "wss://{host}:5000/v1/api/ws"
    _ready_url: str = "http://{host}:5001/readyz"
    _live_url: str = "http://{host}:5001/livez"
    _timeouts = (5.0, 30.0)  # requests connection and read timeouts
    _session: requests.Session
    _use_ibeam: bool
    _user: dict
    _accounts: dict
    _account_id: str

    def __init__(self, use_ibeam: bool = True, host: Optional[str] = None):
        self._session = requests.Session()
        self._use_ibeam = use_ibeam

        if use_ibeam:
            if host is None:
                host = "ibeam"
            data = socket.gethostbyname_ex(host)
            host = data[2][0]
            self._log.debug(f"ibeam ip = {host}")
        elif host is None:
            host = "localhost"

        self._api_url = self._api_url.format(host=host)
        self._ws_url = self._ws_url.format(host=host)
        self._ready_url = self._ready_url.format(host=host)
        self._live_url = self._live_url.format(host=host)

        # test gateway
        if self._use_ibeam:
            self._log.debug("Testing gateway...")
            if not self.is_gateway_ready():
                self._log.warning("Gateway not ready")
                return
            self._log.warning("Gateway ready")
        # get user
        self._user = self.get_user()
        username = self._user["username"]
        paper = self._user["ispaper"]
        self._log.debug(f"Username = {username}, paper = {paper}")
        # get accounts, necessary to initialize internal GW things I think
        self._accounts = self.get_accounts()
        # get portfolio accounts
        accounts = self.get_portfolio_accounts()
        # use the first one
        self._account_id = accounts[0]["accountId"]

    def log(self) -> logging.Logger:
        """Get access to internal logger instance."""
        return self._log

    def request(self, method: str, url: str, **kwargs) -> Union[list, dict]:
        ret = self._session.request(method, self._api_url + url, verify=False, timeout=self._timeouts, **kwargs)
        try:
            ret.raise_for_status()
        except:
            self._log.warning(f"Returned content = '{ret.text}'")
            raise
        return json.loads(ret.text)

    def is_gateway_ready(self) -> bool:
        """Is IB gateway running and authenticated?

        Valid only if using ibeam.
        """
        if not self._use_ibeam:
            # assume always ok
            return True
        try:
            ret = self._session.get(self._ready_url, timeout=2)
            return ret.status_code == 200
        except ConnectTimeout:
            self._log.warning("Timeout")
            return False

    def is_gateway_live(self) -> bool:
        """Is IB gateway alive?

        Valid only if using ibeam.
        """
        if not self._use_ibeam:
            # assume always ok
            return True
        try:
            ret = self._session.get(self._live_url, timeout=2)
            return ret.status_code == 200
        except ConnectTimeout:
            self._log.warning("Timeout")
            return False

    def set_account_id(self, account_id: str):
        """Manually set the account ID to use internally."""
        self._account_id = account_id

    def ping_gateway(self):
        """Ping gateway to keep connection alive."""
        ret = self.request("get", "tickle")
        status = GatewayStatus(**ret)
        if not status.connected or not status.authenticated:
            self._log.warning(status)
        self._log.debug(f"Connected = {status.connected}, authenticated = {status.authenticated}")

    def send_websocket(self, cmd: Union[List[str], str]):
        sslopt = {"cert_reqs": ssl.CERT_NONE}
        ws = create_connection(self._ws_url, sslopt=sslopt)

        ret = ws.recv()
        self._log.debug(f"[ws] {ret}")
        ret = ws.recv()
        self._log.debug(f"[ws] {ret}")

        if isinstance(cmd, str):
            ws.send(cmd)
            self._log.debug(f"[ws] {ret}")
        else:
            for c in cmd:
                ws.send(c)
                self._log.debug(f"[ws] {ret}")

        ws.close()

    def get_user(self) -> dict:
        """
        {'accts': {'DUxxx': {'clearingStatus': 'O',
                                 'isFAClient': False,
                                 'isFunded': True,
                                 'openDate': 1573772400000,
                                 'tradingPermissions': ['OPT',
                                                        'FUT',
                                                        'IOPT',
                                                        'BILL',
                                                        'WAR',
                                                        'STK',
                                                        'CASH',
                                                        'BOND',
                                                        'COMB']}},
         'applicants': [{'businessType': 'INDEPENDENT',
                         'entityId': 10xxx,
                         'id': 50xxx,
                         'legalCountry': {'alpha3': 'CHE', 'name': 'Switzerland'},
                         'nlcode': 'en',
                         'type': 'INDIVIDUAL'}],
         'features': {'bond': True,
                      'calendar': True,
                      'env': 'PROD',
                      'newMf': True,
                      'optionChains': True,
                      'realtime': True,
                      'wlms': True},
         'has2fa': False,
         'islite': False,
         'ispaper': True,
         'props': {'isIBAMClient': False, 'readOnlySession': None},
         'uar': {'accountDetails': True,
                 'forum': True,
                 'fyi': True,
                 'messageCenter': True,
                 'portfolioAnalyst': True,
                 'recentTransactions': True,
                 'tradingRestrictions': False,
                 'tws': True,
                 'userInfo': True,
                 'voting': True},
         'username': 'xxx',
         'wbId': ''}
        """
        return self.request("get", "one/user")

    def get_accounts(self):
        """
        {'accounts': ['DUxxx'],
         'acctProps': {'DUxxx': {'hasChildAccounts': False,
                                     'supportsCashQty': True,
                                     'supportsFractions': False}},
         'aliases': {'DUxxx': 'DUxxx'},
         'allowFeatures': {'allowFXConv': True,
                           'allowFinancialLens': False,
                           'allowMTA': True,
                           'allowTypeAhead': True,
                           'allowedAssetTypes': 'STK,CFD,OPT,FOP,WAR,FUT,BAG,PDC,CASH,IND,BOND,BILL,FUND,SLB,News,CMDTY,IOPT,ICU,ICS,PHYSS,CRYPTO',
                           'debugPnl': True,
                           'liteUser': False,
                           'research': True,
                           'showGFIS': True,
                           'showImpactDashboard': True,
                           'showTaxOpt': True,
                           'showWebNews': True,
                           'snapshotRefreshTimeout': 30},
         'chartPeriods': {'BOND': ['*'],
                          'CASH': ['*'],
                          'CFD': ['*'],
                          'CMDTY': ['*'],
                          'CRYPTO': ['*'],
                          'FOP': ['2h', '1d', '2d', '1w', '1m'],
                          'FUND': ['*'],
                          'FUT': ['*'],
                          'IND': ['*'],
                          'IOPT': ['*'],
                          'OPT': ['2h', '1d', '2d', '1w', '1m'],
                          'PHYSS': ['*'],
                          'STK': ['*'],
                          'WAR': ['*']},
         'groups': [],
         'profiles': [],
         'selectedAccount': 'DUxxx',
         'serverInfo': {'serverName': 'JifZ15032',
                        'serverVersion': 'Build 10.17.1r, Aug 22, 2022 2:57:24 PM'},
         'sessionId': '6305a5a8.0000002f'}
        """
        ret = self.request("get", "iserver/accounts")
        return ret

    def get_portfolio_accounts(self):
        """
        [{'accountAlias': None,
          'accountId': 'DUxxx',
          'accountStatus': 1573772400000,
          'accountTitle': 'xxx',
          'accountVan': 'DUxxx',
          'clearingStatus': 'O',
          'covestor': False,
          'currency': 'CHF',
          'desc': 'DUxxx',
          'displayName': 'xxx',
          'faclient': False,
          'ibEntity': 'IB-UK',
          'id': 'DUxxx',
          'parent': {'accountId': '',
                     'isMChild': False,
                     'isMParent': False,
                     'isMultiplex': False,
                     'mmc': []},
          'tradingType': 'STKNOPT',
          'type': 'DEMO'}]
        """
        ret = self.request("get", "portfolio/accounts")
        return ret

    def get_pnl(self):
        """
        {'upnl': {'Uxxx.Core': {'rowType': 1,
           'dpl': -957.2,
           'nl': 37670.0,
           'upl': -2713.0,
           'el': 24520.0,
           'mv': 42320.0}}}
        """
        ret = self.request("get", "iserver/account/pnl/partitioned")
        return ret

    def get_trades(self):
        ret = self.request("get", "iserver/account/trades")
        return ret

    def get_positions(self, account_id: Optional[str] = None):
        """
        {'acctId': 'U3409871',
          'conid': 577123157,
          'contractDesc': 'SPX    AUG2022 4115 P [SPXW  220822P04115000 100]',
          'position': -1.0,
          'mktPrice': 1.22937835,
          'mktValue': -122.94,
          'currency': 'USD',
          'avgCost': 100.36085,
          'avgPrice': 1.0036085,
          'realizedPnl': 0.0,
          'unrealizedPnl': -22.58,
          'exchs': None,
          'expiry': None,
          'putOrCall': None,
          'multiplier': None,
          'strike': 0.0,
          'exerciseStyle': None,
          'conExchMap': [],
          'assetClass': 'OPT',
          'undConid': 0},
        """
        if account_id is None:
            account_id = self._account_id
        ret = self.request("get", f"portfolio/{account_id}/positions")
        return ret

    def search_futures(self, symbols: List[str]) -> dict:
        """Get list of futures from symbols with various maturity dates."""
        params = {"symbols": ",".join(symbols)}
        ret = self.request("get", "trsrv/futures", params=params)
        return ret

    def search_security(self, symbol: str, sec_type: str) -> List[dict]:
        """
        {'conid': 416904,
        'companyHeader': 'S&P 500 Stock Index - CBOE',
        'companyName': 'S&P 500 Stock Index',
        'symbol': 'SPX',
        'description': 'CBOE',
        'restricted': None,
        'fop': None,
        'opt': '20220822;20220823;20220824;20220825;20220826;20220829;20220830;20220831;20220901;20220902;20220906;20220907;20220909;20220912;20220914;20220915;20220916;20220919;20220923;20220930;20221007;20221020;20221021;20221031;20221117;20221118;20221130;20221215;20221216;20221230;20230119;20230120;20230131;20230216;20230316;20230331;20230420;20230518;20230615;20230630;20230720;20230817;20230914;20231214;20240620;20241219;20251218;20261217;20271216',
        'war': '20210513;20210514;20210812;20210819;20211007;20211124;20211220;20211227;20220124;20220202;20220209;20220218;20220221;20220223;20220224;20220303;20220314;20220316;20220329;20220401;20220404;20220405;20220406;20220407;20220412;20220421;20220426;20220504;20220511;20220513;20220516;20220518;20220519;20220523;20220613;20220614;20220615;20220616;20220617;20220620;20220622;20220701;20220704;20220706;20220707;20220712;20220713;20220714;20220715;20220719;20220720;20220721;20220722;20220726;20220728;20220729;20220802;20220803;20220805;20220811;20220812;20220816;20220817;20220825;20220901;20220908;20220909;20220912;20220913;20220915;20220916;20220922;20220929;20221017;20221020;20221021;20221114;20221117;20221118;20221212;20221213;20221214;20221215;20221216;20221229;20230119;20230216;20230313;20230314;20230316;20230317;20230330;20230420;20230518;20230612;20230613;20230615;20230616;20230629;20230720;20230817;20230912;20230914;20231211;20231212;20231214;20231215;20240312;20240314;20240618;20240620;20241217;20241219;20251218',
        'sections': [{'secType': 'IND', 'exchange': 'CBOE;'},
        {'secType': 'OPT',
        'months': 'AUG22;SEP22;OCT22;NOV22;DEC22;JAN23;FEB23;MAR23;APR23;MAY23;JUN23;JUL23;AUG23;SEP23;DEC23;JUN24;DEC24;DEC25;DEC26;DEC27',
        'exchange': 'SMART;CBOE'},
        {'secType': 'WAR',
        'months': 'MAY21;AUG21;OCT21;NOV21;DEC21;JAN22;FEB22;MAR22;APR22;MAY22;JUN22;JUL22;AUG22;SEP22;OCT22;NOV22;DEC22;JAN23;FEB23;MAR23;APR23;MAY23;JUN23;JUL23;AUG23;SEP23;DEC23;MAR24;JUN24;DEC24;DEC25',
        'exchange': 'BVME;FWB;GETTEX;SBF;SEHK;SWB'},
        {'secType': 'IOPT'},
        {'secType': 'BAG'}]}
        """
        params = {"symbol": symbol, "secType": sec_type}
        ret = self.request("get", "iserver/secdef/search", params=params)
        return ret

    def get_contract_info(self, conid: int) -> ContractInfo:
        """Get contract info from contract ID."""
        ret = self.request("get", f"iserver/contract/{conid}/info")
        return ContractInfo(**ret)

    def get_options_info(self, conid: int, expiration: str, strike: float) -> List[OptionInfo]:
        """Get list of option info.

        NOTE: set strike = 0.0 to get all options.
        """
        month = expiration_to_month(expiration)
        params = {"conid": conid, "secType": "OPT", "month": month, "strike": strike}
        ret = self.request("get", "iserver/secdef/info", params=params)

        opts = [OptionInfo(**r) for r in ret if r["maturityDate"] == expiration]
        return opts

    def get_option_strikes(self, conid: int, expiration: str) -> OptionStrikes:
        month = expiration_to_month(expiration)
        params = {"conid": conid, "secType": "OPT", "month": month}
        strikes = self.request("get", "iserver/secdef/strikes", params=params)
        return OptionStrikes(**strikes)

    @staticmethod
    def get_closest_strike(strikes: OptionStrikes, value: float) -> Tuple[int, float]:
        strike_idx = 0
        strike = 0.0
        for strike_idx in range(len(strikes.call) - 1, -1, -1):
            strike = strikes.call[strike_idx]
            if strike <= value:
                return strike_idx, strike
        raise Exception(f"Strike close to {value} not found")

    def get_option_chain(self, conid: int, expiration: str) -> OptionChain:
        opts = self.get_options_info(conid=conid, expiration=expiration, strike=0.0)
        return OptionChain(call={float(opt.strike): opt for opt in opts if opt.right == "C"},
                           put={float(opt.strike): opt for opt in opts if opt.right == "P"})

    def get_market_history(self, conid: int, period: str = "30d", bar: str = "5min",
                           exchange: Optional[str] = None, outside_rth: bool = True) -> MarketHistory:
        params = {
            'conid': conid,
            'period': period,
            'bar': bar,
            'exchange': exchange,
            'outsideRth': outside_rth
        }
        ret = self.request("get", "iserver/marketdata/history", params=params)

        # start_time = ret["startTime"]
        candles = ret["data"]
        self._log.debug(f"{len(candles)} candles received")
        return MarketHistory(**ret)

    def get_market_history_df(self, *args, **kwargs) -> pd.DataFrame:
        """Get market data history, returning a pandas DataFrame with the candles."""
        ret = self.get_market_history(*args, **kwargs)
        candles = ret.data
        df = pd.DataFrame(candles)
        return df

    @staticmethod
    def get_market_data_fields(def_fields: str = "STK") -> List[str]:
        """Helper function to get default market data default fields."""
        fields = [
            MarketDataFields.Symbol.value,
            MarketDataFields.LastPrice.value,
            MarketDataFields.AskPrice.value,
            MarketDataFields.BidPrice.value,
            MarketDataFields.Volume.value,
            MarketDataFields.Mark.value,
            MarketDataFields.ChangePercent.value,
            MarketDataFields.ChangeSinceOpen.value
        ]
        if def_fields == "OPT":
            fields += [
                MarketDataFields.Delta.value,
                MarketDataFields.Theta.value,
                MarketDataFields.Gamma.value,
                MarketDataFields.Vega.value,
                MarketDataFields.OptionOpenInterest.value,
                MarketDataFields.OptionImpliedVolatilityPercent.value,
                MarketDataFields.OptionVolume.value
            ]
        return fields

    def subscribe_market_data(self, conid: Union[int, List[int]], fields: Optional[List[str]] = None,
                              def_fields: str = "STK"):
        """Subscribe for realtime market data of a contract ID.

        Need to subscribe by sending a command through websocket. Then, the feed
        will be available even from the REST API snapshot endpoints.
        """
        if fields is None:
            fields = self.get_market_data_fields(def_fields=def_fields)

        params = {
            "fields": fields
        }

        # make a list of conids
        if isinstance(conid, int):
            conid = [conid]
        # build commands
        cmds = [
            "smd+" + str(c) + "+" + json.dumps(params).replace(" ", "")
            for c in conid
        ]
        # send websocket commands
        self.send_websocket(cmds)

    def unsubscribe_all_market_data(self):
        """
        {'unsubscribed': True}
        """
        return self.request("get", "iserver/marketdata/unsubscribeall")

    def get_market_data_snapshot(self, conid: Union[int, List[int]]) -> List[dict]:
        # NOTE: assuming to have all fields for which we already subscribed
        # fields = self.get_market_data_fields(fields=fields, def_fields=def_fields)
        # make sure it's a list
        if isinstance(conid, int):
            conid = [conid]
        conid = [str(c) for c in conid]
        params = {
            "conids": ",".join(conid),
            # "fields": ",".join(fields)
        }
        ret = self.request("get", "iserver/marketdata/snapshot", params=params)
        # parse fields, to give meaningful names to field numbers
        ret2 = [
            {
                market_data_fields_map.get(key, key): val
                for key, val in r.items()
            }
            for r in ret
        ]
        return ret2

    def get_orders(self) -> List[Order]:
        """Get open orders."""
        ret = self.request("get", "iserver/account/orders")
        # sometimes it returns an empty array even if there are orders
        if len(ret) == 0:
            # retry once
            ret = self.request("get", "iserver/account/orders")
        return [Order(**order) for order in ret["orders"]]

    def submit_order(self, orders: List[dict], account_id: Optional[str] = None):
        if account_id is None:
            account_id = self._account_id

        # submit orders
        data = {
            "orders": orders
        }
        ret = self.request("post", f"iserver/account/{account_id}/orders", json=data)

        # [{'id': '74d457e7-4225-47a2-a4aa-2660fdb307d9',
        #   'isSuppressed': False,
        #   'message': ['The following order "BUY 1 AAPL NASDAQ.NMS @ 100.00" price '
        #               'exceeds \n'
        #               'the Percentage constraint of 3%.\n'
        #               'Are you sure you want to submit this order?'],
        #   'messageIds': ['o163']}]

        # [{'encrypt_message': '1',
        #   'order_id': '884472628',
        #   'order_status': 'Submitted',
        #   'text': 'Order BUY 1 AAPL NASDAQ.NMS Limit 100.00 will be automatically '
        #           'canceled at 20230101 06:00:00 MET',
        #   'warning_message': '118'}]

        # need to check and eventually reply to all possible questions
        order_ids = []
        while len(ret) > 0:
            # get first item to check
            item = ret.pop(0)
            # check if we have a question
            if "message" in item:
                message = " ".join(item["message"]).replace("\n", " ").replace("  ", " ")
                self._log.debug(f"Question submitting order: {message}")
                reply_id = item["id"]
                data = {
                    "confirmed": True
                }
                ret2 = self.request("post", f"iserver/reply/{reply_id}", json=data)
                # add new items to the list of items to check
                ret += ret2
            elif "order_id" in item:
                order_id = item["order_id"]
                order_status = item["order_status"]
                text = item.get("text")
                self._log.info(f"Order {order_id} {order_status}: {text}")
                order_ids.append(order_id)
            else:
                self._log.error(f"Cannot parse item: '{item}'")
        return order_ids
