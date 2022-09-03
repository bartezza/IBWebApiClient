
from enum import Enum
from typing import List, Optional
from datetime import datetime
from .models import OrderSide, OrderTIF


def build_bracket_order(conid: int, side: OrderSide, price: float, quantity: int,
                        price_profit: Optional[float], price_loss: Optional[float],
                        coid: Optional[str] = None, outside_rth: bool = False,
                        tif: OrderTIF = OrderTIF.DAY) -> List[dict]:
    """Build bracket order.

    Args:
        conid: Contract ID.
        side: buy/sell.
        price: Limit price at which to buy/sell.
        quantity: Quantity to buy/sell.
        price_profit: Take profit limit price (set to None to disable).
        price_loss: Stop loss price at which a stop market order is issued (set to None to disable).
        coid: Optional custom order ID.
        outside_rth: Outside regular trading hours?
        tif: Order time-in-force.

    Returns:
        List of orders to submit.
    """

    if coid is None:
        now = datetime.now()
        coid = f"my_order_{now.hour}_{now.minute}_{now.second}"

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
    orders = [order]

    close_side = OrderSide.get_opposite(side)

    if price_profit is not None:
        # check price
        if side == OrderSide.BUY:
            assert price_profit > price
        else:
            assert price_profit < price

        take_profit = order.copy()
        take_profit.update({
            "orderType": "LMT",  # "LMT", "MKT", "STP", "STOP_LIMIT", "MIDPRICE", "TRAIL", "TRAILLMT"
            "price": price_profit,
            "side": close_side.value,
            "referrer": "TakeProfitOrder",
            "parentId": coid,
            "cOID": None
        })
        orders.append(take_profit)

    if price_loss is not None:
        # check price
        if side == OrderSide.BUY:
            assert price_loss < price
        else:
            assert price_loss > price

        stop_loss = order.copy()
        stop_loss.update({
            "orderType": "STP",  # "LMT", "MKT", "STP", "STOP_LIMIT", "MIDPRICE", "TRAIL", "TRAILLMT"
            "price": price_loss,
            "side": close_side.value,
            "referrer": "StopLossOrder",
            "parentId": coid,
            "cOID": None
        })
        orders.append(stop_loss)
    return orders


def build_exit_strategy(conid: int, close_side: OrderSide, quantity: int,
                        price_profit: Optional[float], price_loss: Optional[float],
                        coid: Optional[str] = None, outside_rth: bool = False,
                        tif: OrderTIF = OrderTIF.DAY) -> List[dict]:
    """Build OCA orders with take profit and stop loss.

    Args:
        conid: Contract ID.
        close_side: Side of the closing orders.
        quantity: Quantity to buy/sell.
        price_profit: Optional price for take profit.
        price_loss: Optional price for stop loss.
        coid: Optional custom order ID.
        outside_rth: Outside regular trading hours?
        tif: Order time-in-force.

    Returns:
        List of orders to submit.
    """

    orders = []
    if price_profit is not None:
        take_profit = {
            "conid": conid,
            # "secType":  "265598:STK",
            # "cOID":  "66827301",
            "orderType": "LMT",
            # "listingExchange": "SMART",
            "outsideRTH": outside_rth,
            "price": price_profit,
            "side": close_side.value,
            # "ticker":  "AAPL",
            "tif": tif.value,
            "referrer": "TakeProfitOrder",
            "quantity": quantity,
            "useAdaptive": False,
            "isClose": False,
            # "isSingleGroup": True  # set eventually later
        }
        orders.append(take_profit)

    if price_loss is not None:
        stop_loss = {
            # "acctId":  "DU***14 ",
            "conid": conid,
            # "secType":  "8314:STK ",
            # "cOID":  "66827302 ",
            "orderType": "STP",
            # "listingExchange":  "SMART",
            "outsideRTH": outside_rth,
            "price": price_loss,
            "side": close_side.value,
            # "ticker":  "IBML",
            "tif": tif.value,
            "referrer": "StopLossOrder",
            "quantity": quantity,
            "useAdaptive": False,
            "isClose": False,
            # "isSingleGroup": True,  # set eventually later
        }
        orders.append(stop_loss)

    # set orders as OCA if more than one
    if len(orders) > 1:
        for order in orders:
            order["isSingleGroup"] = True

    return orders
