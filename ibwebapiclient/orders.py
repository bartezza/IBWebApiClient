
from enum import Enum
from typing import List, Optional
from datetime import datetime


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


class OrderTIF(Enum):
    GTC = "GTC"
    OPG = "OPG"
    DAY = "DAY"
    IOC = "IOC"


def build_bracket_order(conid: int, side: OrderSide, price: float, quantity: int,
                        price_profit: float, price_loss: float,
                        coid: Optional[str] = None, outside_rth: bool = False,
                        tif: OrderTIF = OrderTIF.DAY) -> List[dict]:
    """Build bracket order.

    Args:
        conid: Contract ID.
        coid: Optional custom order ID.
    """

    if coid is None:
        now = datetime.now()
        coid = f"my_order_{now.hour}_{now.minute}_{now.second}"

    if side == OrderSide.SELL:
        close_side = OrderSide.BUY
        # check
        assert price_profit < price < price_loss
    elif side == OrderSide.BUY:
        close_side = OrderSide.SELL
        # check
        assert price_profit > price > price_loss
    else:
        raise ValueError

    order = {
        # "accId"
        "conid": conid,
        "cOID": coid,
        # "parentId"
        "orderType": "LMT",  # "LMT", "MKT", "STP", "STOP_LIMIT", "MIDPRICE", "TRAIL", "TRAILLMT"
        # "listingExchange"
        # "isSingleGroup"  # for OCA
        "outsideRTH": outside_rth,
        "price": price,
        # "auxPrice"
        "side": side.value,  # "BUY", "SELL"
        # "ticker": "AAPL",
        "tif": tif.value,  # "GTC", "OPG" (Open Price Guarantee), "DAY", "IOC"
        # "trailingAmt"
        # ...
        "quantity": quantity,
        # "useAdaptive": False
    }

    take_profit = order.copy()
    take_profit.update({
        "orderType": "LMT",  # "LMT", "MKT", "STP", "STOP_LIMIT", "MIDPRICE", "TRAIL", "TRAILLMT"
        "price": price_profit,
        "side": close_side.value,
        "referrer": "TakeProfitOrder",
        "parentId": coid,
        "cOID": None
    })

    stop_loss = order.copy()
    stop_loss.update({
        "orderType": "STP",  # "LMT", "MKT", "STP", "STOP_LIMIT", "MIDPRICE", "TRAIL", "TRAILLMT"
        "price": price_loss,
        "side": close_side.value,
        "referrer": "StopLossOrder",
        "parentId": coid,
        "cOID": None
    })
    return [order, take_profit, stop_loss]
