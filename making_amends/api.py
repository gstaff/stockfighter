import json
import requests
import websocket
import thread
import time
from pprint import pprint
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

API_KEY = "3dbd325cb22f0c2dd734ea3d7b9d49ea1bc29af1"
API_HEADERS = {"X-Starfighter-Authorization": API_KEY}


class Direction:
    BUY = "buy"
    SELL = "sell"

    def __init__(self):
        pass


class Orders:
    LIMIT = "limit"
    MARKET = "market"
    FOK = "fill-or-kill"
    IOC = "immediate-or-cancel"

    def __init__(self):
        pass


def get_heartbeat():
    """
    Result Format
    {
      "ok": true,
      "error": ""
    }
    """
    response = requests.get("https://api.stockfighter.io/ob/api/heartbeat", headers=API_HEADERS)
    response.raise_for_status()
    json = response.json()
    return json


def get_venue_heartbeat(venue):
    """
    Result Format
    {
      "ok": true,
      "venue": "TESTEX"
    }
    :param venue: The venue symbol (e.g. OGEX for Ogaki Stock Exchange)
    """
    response = requests.get("https://api.stockfighter.io/ob/api/venues/{0}/heartbeat".format(venue),
                            headers=API_HEADERS)
    response.raise_for_status()
    json = response.json()
    return json


def get_stocks(venue):
    """
    Result Format
    {
      "ok": true,
      "symbols": [
        {
          "name": "Foreign Owned Occulmancy",
         "symbol": "FOO"
        },
        {
          "name": "Best American Ricecookers",
          "symbol": "BAR"
        },
        {
          "name": "Badly Aliased Zebras",
          "symbol": "BAZ"
        }
      ]
    }
    :param venue:
    """
    response = requests.get("https://api.stockfighter.io/ob/api/venues/{0}/stocks".format(venue))
    response.raise_for_status()
    json = response.json()
    return json


def get_orderbook(venue, stock):
    """
    Result Format
    {
      "ok": true,
      "venue": "OGEX",
      "symbol": "FAC",
      "bids":
        [
          {"price": 5200, "qty": 1, "isBuy": true},
          ...
          ...
          ...
          {"price": 815, "qty": 15, "isBuy": true},
          {"price": 800, "qty": 12, "isBuy": true},
          {"price": 800, "qty": 152, "isBuy": true}
        ],
      "asks":
       [
          {"price": 5205, "qty": 150, "isBuy": false},
          {"price": 5205, "qty": 1, "isBuy": false},
          ...
          ...
          ...
          {"price": 1000000000000, "qty": 99999, "isBuy": false}
       ],
      "ts": "2015-12-04T09:02:16.680986205Z" // timestamp we grabbed the book at
    }
    :param stock:
    :param venue:
    """
    response = requests.get("https://api.stockfighter.io/ob/api/venues/{0}/stocks/{1}".format(venue, stock))
    response.raise_for_status()
    json = response.json()
    return json


def post_order(account, venue, stock, price, qty, direction, order_type):
    """
    Result Format
    {
      "ok": true,
      "symbol": "FAC",
      "venue": "OGEX",
      "direction": "buy",
      "originalQty": 100,
      "qty": 20,   // this is the quantity *left outstanding*
      "price":  5100, // the price on the order -- may not match that of fills!
      "orderType": "limit",
      "id": 12345, // guaranteed unique *on this venue*
      "account" : "OGB12345",
      "ts": "2015-07-05T22:16:18+00:00", // ISO-8601 timestamp for when we received order
      "fills":
        [
          {
            "price": 5050,
            "qty": 50
            "ts": "2015-07-05T22:16:18+00:00"
          }, ... // may have zero or multiple fills.  Note this order presumably has a total of 80 shares worth
        ],
      "totalFilled": 80,
      "open": true
    }
    :param order_type:
    :param direction:
    :param qty:
    :param price:
    :param stock:
    :param venue:
    :param account:
    """
    payload = {
        "account": account,
        "price": price,
        "qty": qty,
        "direction": direction,
        "orderType": order_type
    }
    response = requests.post("https://api.stockfighter.io/ob/api/venues/{0}/stocks/{1}/orders".format(venue, stock),
                             headers=API_HEADERS,
                             json=payload)
    response.raise_for_status()
    json = response.json()
    return json


def get_quote(venue, stock):
    """
    Result Format
    {
      "ok": true,
      "venue": "OGEX",
      "symbol": "FAC",
      "bids":
        [
          {"price": 5200, "qty": 1, "isBuy": true},
          ...
          ...
          ...
          {"price": 815, "qty": 15, "isBuy": true},
          {"price": 800, "qty": 12, "isBuy": true},
          {"price": 800, "qty": 152, "isBuy": true}
        ],
      "asks":
       [
          {"price": 5205, "qty": 150, "isBuy": false},
          {"price": 5205, "qty": 1, "isBuy": false},
          ...
          ...
          ...
          {"price": 1000000000000, "qty": 99999, "isBuy": false}
       ],
      "ts": "2015-12-04T09:02:16.680986205Z" // timestamp we grabbed the book at
    }
    :param venue:
    :param stock:
    :return:
    """
    response = requests.get("https://api.stockfighter.io/ob/api/venues/{0}/stocks/{1}/quote".format(venue, stock),
                            headers=API_HEADERS)
    response.raise_for_status()
    json = response.json()
    return json


def get_order(venue, stock, order_id):
    """
    Result Format
    {
      "ok": true,
      "symbol": "ROBO",
      "venue": "ROBUST",
      "direction": "buy",
      "originalQty": 85,
      "qty": 40,
      "price": 993,
      "orderType": "immediate-or-cancel",
      "id": 1,
      "account": "FOO123",
      "ts": "2015-08-10T16:10:32.987288+09:00",
      "fills": [
        {
          "price": 366,
          "qty": 45,
          "ts": "2015-08-10T16:10:32.987292+09:00"
        }
      ],
      "totalFilled": 85,
      "open": true
    }
    :param venue:
    :param stock:
    :param order_id:
    :return:
    """
    response = requests.get("https://api.stockfighter.io/ob/api/venues/{0}/stocks/{1}/orders/{2}"
                            .format(venue, stock, order_id),
                            headers=API_HEADERS)
    response.raise_for_status()
    json = response.json()
    return json


def delete_order(venue, stock, order_id):
    """
    Result Format
    {
      "ok": true,
      "symbol": "ROBO",
      "venue": "ROBUST",
      "direction": "buy",
      "originalQty": 85,
      "qty": 40,
      "price": 993,
      "orderType": "immediate-or-cancel",
      "id": 1,
      "account": "FOO123",
      "ts": "2015-08-10T16:10:32.987288+09:00",
      "fills": [
        {
          "price": 366,
          "qty": 45,
          "ts": "2015-08-10T16:10:32.987292+09:00"
        }
      ],
      "totalFilled": 85,
      "open": true
    }
    :param venue:
    :param stock:
    :param order_id:
    :return:
    """
    response = requests.delete("https://api.stockfighter.io/ob/api/venues/{0}/stocks/{1}/orders/{2}"
                               .format(venue, stock, order_id),
                               headers=API_HEADERS)
    response.raise_for_status()
    json = response.json()
    return json


def get_account_orders(venue, account):
    """
    Result Format
    {
      "ok": true,
      "venue": "ROBUST",
      "orders": [
        {
          "symbol": "ROBO",
          "venue": "ROBUST",
          "direction": "buy",
          "originalQty": 85,
          "qty": 40,
          "price": 993,
          "orderType": "immediate-or-cancel",
          "id": 1,
          "account": "FOO123",
          "ts": "2015-08-10T16:10:32.987288+09:00",
          "fills": [
            {
              "price": 366,
              "qty": 45,
              "ts": "2015-08-10T16:10:32.987292+09:00"
            }
          ],
          "totalFilled": 85,
          "open": true
        },
        ... // We'll show any number of orders.
      ]
    }
    :param venue:
    :param account:
    :return:
    """
    response = requests.get("https://api.stockfighter.io/ob/api/venues/{0}/accounts/{1}/orders".format(venue, account),
                            headers=API_HEADERS)
    response.raise_for_status()
    json = response.json()
    return json


def get_stock_orders(venue, account, stock):
    """
    Result Format
    {
      "ok": true,
      "venue": "ROBUST",
      orders: [
        {
          "symbol": "ROBO",
          "venue": "ROBUST",
          "direction": "buy",
          "originalQty": 85,
          "qty": 40,
          "price": 993,
          "orderType": "immediate-or-cancel",
          "id": 1,
          "account": "FOO123",
          "ts": "2015-08-10T16:10:32.987288+09:00",
          "fills": [
            {
              "price": 366,
              "qty": 45,
              "ts": "2015-08-10T16:10:32.987292+09:00"
            }
          ],
          "totalFilled": 85,
          "open": true
        },
        ... // We'll show any number of orders.
      ]
    }
    :param venue:
    :param account:
    :param stock:
    :return:
    """
    response = requests.get("https://api.stockfighter.io/ob/api/venues/{0}/accounts/{1}/stocks/{2}/orders"
                            .format(venue, account, stock),
                            headers=API_HEADERS)
    response.raise_for_status()
    json = response.json()
    return json


def on_message(ws, message):
    pprint(json.loads(message))


def on_error(ws, error):
    pprint(error)


def on_close(ws):
    pprint("### Closed Websocket ###")


def on_open(ws):
    def run(*args):
        time.sleep(1)
        pprint("### Opening Websocket ###")
        # time.sleep(5)
        # ws.close()
        print "thread terminating..."

    thread.start_new_thread(run, ())


def connect_to_quotes_feed(trading_account, venue, stock=None):
    """
    Result Format
    {
      "ok": true,
      "quote": { // the below is the same as returned through the REST quote API
        "symbol": "FAC",
        "venue": "OGEX",
        "bid": 5100, // best price currently bid for the stock
        "ask": 5125, // best price currently offered for the stock
        "bidSize": 392, // aggregate size of all orders at the best bid
        "askSize": 711, // aggregate size of all orders at the best ask
        "bidDepth": 2748, // aggregate size of *all bids*
        "askDepth": 2237, // aggregate size of *all asks*
        "last": 5125, // price of last trade
        "lastSize": 52, // quantity of last trade
        "lastTrade": "2015-07-13T05:38:17.33640392Z", // timestamp of last trade,
        "quoteTime": "2015-07-13T05:38:17.33640392Z" // server ts of quote generation
      }
    }
    :param trading_account:
    :param venue:
    :param stock:
    :return:
    """
    if stock:
        request = "wss://api.stockfighter.io/ob/api/ws/{0}/venues/{1}/tickertape/stocks/{2}" \
            .format(trading_account, venue, stock)
    else:
        request = "wss://api.stockfighter.io/ob/api/ws/{0}/venues/{1}/tickertape".format(trading_account, venue)
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(request,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()


def connect_to_executions_feed(trading_account, venue, stock=None):
    """
    Result Format
    // Note that this is pretty-printed for you, but your web socket library may not respect that
    {
      "ok":true,
      "account": "TAH97715708", // trading account of the participant this execution is for
      "venue":"UYIEX",
      "symbol":"FERE",
      "order":
        {
          "ok": true,
          "symbol":"FERE",
          "venue":"UYIEX",
          "direction":"buy",
          "originalQty":1,
          "qty":0,
          "price":0,
          "orderType":"market",
          "id":30,
          "account":"TAH97715708",
          "ts":"2015-08-10T16:54:25.803619968Z",
          "fills":[
            {
              "price":8332,
              "qty":1,
              "ts":"2015-08-10T16:54:25.803626698Z"
            }
          ],
        "totalFilled":1,
          "open":false
        },
      "standingId":25,
      "incomingId":30,
      "price":8332,
      "filled":1,
      "filledAt":"2015-08-10T16:54:25.803626698Z",
      "standingComplete":false,  // whether the order that was on the book is now complete
      "incomingComplete":true  // whether the incoming order is complete (as of this execution)
    }
    :param trading_account:
    :param venue:
    :param stock:
    :return:
    """
    if stock:
        request = "wss://api.stockfighter.io/ob/api/ws/{0}/venues/{1}/executions/stocks/{2}" \
            .format(trading_account, venue, stock)
    else:
        request = "wss://api.stockfighter.io/ob/api/ws/{0}/venues/{1}/executions".format(trading_account, venue)
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(request,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()

# pprint(get_heartbeat())
# pprint(get_venue_heartbeat("TESTEX"))
# pprint(get_stocks("TESTEX"))
# pprint(get_orderbook("TESTEX", "FOOBAR"))
# pprint(post_order("EXB123456", "TESTEX", "FOOBAR", 100, 10, Direction.BUY, "limit"))
# pprint(get_quote("TESTEX", "FOOBAR"))
# pprint(get_order("TESTEX", "FOOBAR", 154))
# pprint(delete_order("TESTEX", "FOOBAR", 154))
# pprint(get_account_orders("TESTEX", "EXB123456"))
# pprint(get_stock_orders("TESTEX", "EXB123456", "FOOBAR"))
# connect_to_quotes_feed("WSE64529138", "JTOMEX")
# connect_to_quotes_feed("WSE64529138", "JTOMEX", "OLC")
# connect_to_executions_feed("WSE64529138", "JTOMEX")
# connect_to_executions_feed("WSE64529138", "JTOMEX", "OLC")
