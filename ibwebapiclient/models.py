
from enum import Enum
from typing import Optional, List, Dict
from pydantic import BaseModel


class AssetClass(Enum):
    STK = "STK"
    OPT = "OPT"


class OrderStatus(Enum):
    PRESUBMITTED = "PreSubmitted"
    SUBMITTED = "Submitted"
    FILLED = "Filled"
    CANCELLED = "Cancelled"
    INACTIVE = "Inactive"

    @staticmethod
    def is_open(value: str) -> bool:
        return value in ("PreSubmitted", "Submitted")


class OrderType(Enum):
    LMT = "LMT"
    MKT = "MKT"
    STP = "STP"
    STOP_LIMIT = "STOP_LIMIT"
    MIDPRICE = "MIDPRICE"
    TRAIL = "TRAIL"
    TRAILLMT = "TRAILLMT"


class OrderSide(Enum):
    BUY = "BUY"
    SELL = "SELL"

    @staticmethod
    def get_opposite(side: "OrderSide") -> "OrderSide":
        if side == OrderSide.BUY:
            return OrderSide.SELL
        elif side == OrderSide.SELL:
            return OrderSide.BUY
        else:
            raise ValueError(str(side))


class OrderTIF(Enum):
    GTC = "GTC"
    OPG = "OPG"
    DAY = "DAY"
    IOC = "IOC"
    CLOSE = "CLOSE"


class MarketDataFields(Enum):
    """Represents the fields for the `MarketDataSnapshot` service.

    Copyied from interactive-brokers-api repo.
    """

    LastPrice = '31'
    Symbol = '55'
    Text = '58'
    High = '70'
    Low = '71'
    Position = '72'
    MarketValue = '73'
    AvgPrice = '74'
    UnrealizedPnl = '75'
    FormattedPosition = '76'
    FormattedUnrealizedPnl = '77'
    DailyPnl = '78'
    Change = '82'
    ChangePercent = '83'
    BidPrice = '84'
    AskSize = '85'
    AskPrice = '86'
    Volume = '87'
    BidSize = '88'
    Exchange = '6004'
    Conid = '6008'
    SecType = '6070'
    Months = '6072'
    RegularExpiry = '6073'
    Marker = '6119'
    UnderlyingContract = '6457'
    MarketDataAvailability = '6509'
    CompanyName = '7051'
    AskExch = '7057'
    LastExch = '7058'
    LastSize = '7059'
    BidExch = '7068'
    MarketDataAvailabilityOther = '7084'
    PutCallInterest = '7085'
    PutCallVolume = '7086'
    HistoricVolumePercent = '7087'
    HistoricVolumeClosePercent = '7088'
    OptionVolume = '7089'
    ContractIdAndExchange = '7094'
    ContractDescription = '7219'
    ContractDescriptionOther = '7220'
    ListingExchange = '7221'
    Industry = '7280'
    Category = '7281'
    AverageVolume = '7282'
    OptionImpliedVolatilityPercent = '7283'
    HistoricVolume = '7284'
    PutCallRatio = '7285'
    DividendAmount = '7286'
    DividentYield = '7287'
    Ex = '7288'
    MarketCap = '7289'
    PriceEarningsRatio = '7290'
    EarningsPerShare = '7291'
    CostBasis = '7292'
    FiftyTwoWeekLow = '7293'
    FiftyTwoWeekHigh = '7294'
    Open = '7295'
    Close = '7296'
    Delta = '7308'
    Gamma = '7309'
    Theta = '7310'
    Vega = '7311'
    OptionVolumeChangePercent = '7607'
    ImpliedVolatilityPercent = '7633'
    Mark = '7635'
    ShortableShares = '7636'
    FeeRate = '7637'
    OptionOpenInterest = '7638'
    PercentOfMarketValue = '7639'
    Shortable = '7644'
    MorningstarRating = '7655'
    Dividends = '7671'
    DividendsTtm = '7672'
    EMATwoHundred = '7674'
    EMAOneHundred = '7675'
    EMAFiftyDay = '7676'
    EMATwentyDay = '7677'
    PriceEMATwoHundredDay = '7678'
    PriceEMAOneHundredDay = '7679'
    PriceEMAFiftyDay = '7680'
    PriceEMATwentyDay = '7681'
    ChangeSinceOpen = '7682'
    UpcomingEvent = '7683'
    UpcomingEventDate = '7684'
    UpcomingAnalystMeeting = '7685'
    UpcomingEarnings = '7686'
    UpcomingMiscEvents = '7687'
    RecentAnalystMeeting = '7688'
    RecentEarnings = '7689'
    RecentMiscEvents = '7690'
    ProbabilityOfMaxReturnCustomer = '7694'
    BreakEven = '7695'
    SpxDelta = '7696'
    FuturesOpenInterest = '7697'
    LastYield = '7698'
    BidYield = '7699'
    ProbabilityMaxReturn = '7700'
    ProbabilityMaxLoss = '7702'
    ProfitProbability = '7703'
    OrganizationType = '7704'
    DebtClass = '7705'
    Ratings = '7706'
    BondStateCode = '7707'
    BondType = '7708'
    LastTradingDate = '7714'
    IssueDate = '7715'
    Beta = '7718'
    AskYield = '7720'
    PriorClose = '7741'
    VolumeLong = '7762'
    All = [
        '31', '55', '58', '70', '71', '72', '73', '74', '75', '76', '77', '78', '82', '83', '84', '85', '86', '87', '88', '6004', '6008', '6070', '6072', '6073', '6119', '6457', '6509', '7051', '7057', '7058', '7059', '7068', '7084', '7085', '7086', '7087', '7088', '7089', '7094', '7219', '7220', '7221', '7280', '7281', '7282', '7283', '7284', '7285', '7286', '7287', '7288', '7289', '7290', '7291', '7292', '7293', '7294', '7295',
        '7296', '7308', '7309', '7310', '7311', '7607', '7633', '7635', '7636', '7637', '7638', '7639', '7644', '7655', '7671', '7672', '7674', '7675', '7676', '7677', '7678', '7679', '7680', '7681', '7682', '7683', '7684', '7685', '7686', '7687', '7688', '7689', '7690', '7694', '7695', '7696', '7697', '7698', '7699', '7700', '7702', '7703', '7704', '7705', '7706', '7707', '7708', '7714', '7715', '7718', '7720', '7741', '7762'
    ]


# map build with my_convert_fields.py
market_data_fields_map = {
    # added manually:
    "87_raw": "volume_raw",
    # automatically converted:
    "31": "last_price",
    "55": "symbol",
    "58": "text",
    "70": "high",
    "71": "low",
    "72": "position",
    "73": "market_value",
    "74": "avg_price",
    "75": "unrealized_pnl",
    "76": "formatted_position",
    "77": "formatted_unrealized_pnl",
    "78": "daily_pnl",
    "82": "change",
    "83": "change_percent",
    "84": "bid_price",
    "85": "ask_size",
    "86": "ask_price",
    "87": "volume",
    "88": "bid_size",
    "6004": "exchange",
    "6008": "conid",
    "6070": "sec_type",
    "6072": "months",
    "6073": "regular_expiry",
    "6119": "marker",
    "6457": "underlying_contract",
    "6509": "market_data_availability",
    "7051": "company_name",
    "7057": "ask_exch",
    "7058": "last_exch",
    "7059": "last_size",
    "7068": "bid_exch",
    "7084": "market_data_availability_other",
    "7085": "put_call_interest",
    "7086": "put_call_volume",
    "7087": "historic_volume_percent",
    "7088": "historic_volume_close_percent",
    "7089": "option_volume",
    "7094": "contract_id_and_exchange",
    "7219": "contract_description",
    "7220": "contract_description_other",
    "7221": "listing_exchange",
    "7280": "industry",
    "7281": "category",
    "7282": "average_volume",
    "7283": "option_implied_volatility_percent",
    "7284": "historic_volume",
    "7285": "put_call_ratio",
    "7286": "dividend_amount",
    "7287": "divident_yield",
    "7288": "ex",
    "7289": "market_cap",
    "7290": "price_earnings_ratio",
    "7291": "earnings_per_share",
    "7292": "cost_basis",
    "7293": "fifty_two_week_low",
    "7294": "fifty_two_week_high",
    "7295": "open",
    "7296": "close",
    "7308": "delta",
    "7309": "gamma",
    "7310": "theta",
    "7311": "vega",
    "7607": "option_volume_change_percent",
    "7633": "implied_volatility_percent",
    "7635": "mark",
    "7636": "shortable_shares",
    "7637": "fee_rate",
    "7638": "option_open_interest",
    "7639": "percent_of_market_value",
    "7644": "shortable",
    "7655": "morningstar_rating",
    "7671": "dividends",
    "7672": "dividends_ttm",
    "7674": "ema_two_hundred",
    "7675": "ema_one_hundred",
    "7676": "ema_fifty_day",
    "7677": "ema_twenty_day",
    "7678": "price_ema_two_hundred_day",
    "7679": "price_ema_one_hundred_day",
    "7680": "price_ema_fifty_day",
    "7681": "price_ema_twenty_day",
    "7682": "change_since_open",
    "7683": "upcoming_event",
    "7684": "upcoming_event_date",
    "7685": "upcoming_analyst_meeting",
    "7686": "upcoming_earnings",
    "7687": "upcoming_misc_events",
    "7688": "recent_analyst_meeting",
    "7689": "recent_earnings",
    "7690": "recent_misc_events",
    "7694": "probability_of_max_return_customer",
    "7695": "break_even",
    "7696": "spx_delta",
    "7697": "futures_open_interest",
    "7698": "last_yield",
    "7699": "bid_yield",
    "7700": "probability_max_return",
    "7702": "probability_max_loss",
    "7703": "profit_probability",
    "7704": "organization_type",
    "7705": "debt_class",
    "7706": "ratings",
    "7707": "bond_state_code",
    "7708": "bond_type",
    "7714": "last_trading_date",
    "7715": "issue_date",
    "7718": "beta",
    "7720": "ask_yield",
    "7741": "prior_close",
    "7762": "volume_long"
}


class GatewayStatus(BaseModel):
    session: str  # '11fbe1474b90e950ff099f5b2ff07f91'
    ssoExpires: int  # 542578
    collission: bool  # False
    userId: int  # 45209036
    authenticated: bool
    competing: bool
    connected: bool
    message: Optional[str]
    MAC: str
    serverName: Optional[str]
    serverVersion: Optional[str]

    def __init__(self, **kwargs):
        # flat out unnecessary nested dict structure
        super().__init__(**kwargs,
                         **kwargs["iserver"]["authStatus"].get("serverInfo", {}),
                         **kwargs["iserver"]["authStatus"])


class ContractInfo(BaseModel):
    cfi_code: str  # 'OCXXXS',
    symbol: str  # 'SPX',
    cusip: Optional[str]  # None,
    expiry_full: Optional[str]  # '20220822',
    con_id: int  # 577123126,
    maturity_date: Optional[str]  # '20220822',
    instrument_type: str  # 'OPT',
    trading_class: Optional[str]  # 'SPXW',
    valid_exchanges: str  # 'SMART,CBOE',
    allow_sell_long: bool  # False,
    is_zero_commission_security: bool  # False,
    local_symbol: str  # 'SPXW  220822C04230000',
    contract_clarification_type: Optional[str]  # None,
    classifier: Optional[str]  # None,
    currency: str  # 'USD',
    text: Optional[str]  # "(SPXW) AUG 22 '22 4230 Call",
    underlying_con_id: int  # 416904,
    r_t_h: bool  # True,
    multiplier: Optional[str]  # '100',
    strike: Optional[str]  # '4230.0',
    right: Optional[str]  # 'CALL',
    underlying_issuer: Optional[str]  # None,
    contract_month: Optional[str]  # '202208',
    company_name: str  # 'S&P 500 Stock Index',
    smart_available: Optional[bool]  # True,
    exchange: str  # 'SMART'


class OptionInfo(BaseModel):
    conid: int  # 577123126,
    symbol: str  # 'SPX',
    secType: str  # 'OPT',
    exchange: str  # 'SMART',
    listingExchange: Optional[str]  # None,
    right: str  # 'C',
    strike: float  # 4230.0,
    currency: str  # 'USD',
    cusip: Optional[str]  # None,
    coupon: str  # 'No Coupon',
    desc1: str  # 'SPX',
    desc2: str  # "(SPXW) AUG 22 '22 4230 Call",
    maturityDate: str  # '20220822',
    multiplier: str  # '100',
    tradingClass: str  # 'SPXW',
    validExchanges: str  # 'SMART,CBOE'


class OptionStrikes(BaseModel):
    call: List[float]
    put: List[float]


class OptionChain(BaseModel):
    call: Dict[float, OptionInfo]
    put: Dict[float, OptionInfo]


class MarketHistory(BaseModel):
    barLength: int  # 86400,
    data: List[dict]  # [{'c: 4140.83, 'h', 'l', 'o', 't': 1661347800000, 'v': 0}]
    high: str  # '415656/0/1440',
    low: str  # '411997/0/1440',
    mdAvailability: str  # 'S',
    messageVersion: int  # 2,
    mktDataDelay: int  # 0,
    negativeCapable: bool  # False,
    outsideRth: bool  # False,
    points: int  # 0,
    priceDisplayRule: int  # 1,
    priceDisplayValue: str  # '2',
    priceFactor: int  # 100,
    serverId: str  # '12415',
    startTime: str  # '20220823-13:30:00',
    symbol: str  # 'SPX',
    text: str  # 'S&P 500 Stock Index',
    timePeriod: str  # '2d',
    travelTime: int  # 564,
    volumeFactor: int  # 1


class Order(BaseModel):
    acct: str  # 'DUxxx',
    bgColor: str  # '#000000',
    cashCcy: str  # 'USD',
    companyName: str  # 'APPLE INC',
    conid: int  # 265598,
    conidex: str  # '265598',
    description1: str  # 'AAPL',
    fgColor: str  # '#AFAFAF',
    filledQuantity: float  # 0.0,
    lastExecutionTime: str  # '220827093055',
    lastExecutionTime_r: int  # 1661592655000,
    listingExchange: Optional[str]  # 'NASDAQ.NMS',
    orderDesc: str  # 'Buy 1 Limit 100.00 GTC',
    orderId: int  # 1083610844,
    orderType: str  # 'Limit',
    origOrderType: str  # 'LIMIT',
    price: Optional[str]  # '100.00',
    remainingQuantity: float  # 1.0,
    secType: str  # 'STK',
    side: str  # 'BUY',
    sizeAndFills: str  # '0/1',
    status: str  # see OrderStatus
    supportsTaxOpt: str  # '1',
    ticker: str  # 'AAPL',
    timeInForce: str  # 'GTC'

    def is_open(self) -> bool:
        return OrderStatus.is_open(self.status)


class Position(BaseModel):
    acctId: str  # 'U3409871',
    assetClass: str  # 'OPT',
    avgCost: float  # 185.36085,
    avgPrice: float  # 1.8536085,
    conExchMap: list  # [],
    conid: int  # 581288360,
    contractDesc: str  # 'SPX    AUG2022 4045 C [SPXW  220830C04045000 100]',
    currency: str  # 'USD',
    exchs: Optional[str]  # None,
    exerciseStyle: Optional[str]  # None,
    expiry: Optional[str]  # None,
    mktPrice: float  # 0.47615925,
    mktValue: float  # -47.62,
    multiplier: Optional[float]  # None,
    position: float  # -1.0,
    putOrCall: Optional[str]  # None,
    realizedPnl: float  # 0.0,
    strike: float  # 0.0,
    undConid: int  # 0,
    unrealizedPnl: float  # 137.74


class Trade(BaseModel):
    account: str  # 'U3409871',
    accountCode: str  # 'U3409871',
    clearing_id: Optional[str]  # 'IB',
    clearing_name: Optional[str]  # 'IB',
    commission: Optional[str]  # '1.55',
    company_name: str  # 'S&P 500 Stock Index',
    conid: int  # 547639942,
    conidEx: str  # '547639942',
    contract_description_1: str  # 'SPX',
    contract_description_2: Optional[str]  # "(SPXW) AUG 31 '22 4040 Call",
    directed_exchange: str  # 'CBOE',
    exchange: str  # 'CBOE',
    execution_id: str  # '0000f711.630f3d2d.05.01',
    liquidation_trade: str  # '0',
    net_amount: float  # 5.0,
    open_close: Optional[str]  # '???',
    order_description: str  # 'Sold 1 @ 0.05 on CBOE',
    price: str  # '0.05',
    sec_type: str  # 'OPT',
    side: str  # 'S',
    size: float  # 1.0,
    supports_tax_opt: str  # '1',
    symbol: str  # 'SPX',
    trade_time: str  # '20220831-19:03:55',
    trade_time_r: int  # 1661972635000
