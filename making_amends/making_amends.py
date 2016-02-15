import json
import os
import re
from pprint import pprint
import requests
import thread
import time
import websocket
import api

ACCOUNT = "CES37558856"
VENUE = "EUQDEX"
STOCK = "TSI"
EXECUTIONS = {}
QUOTES = []


def check_api():
    pprint(api.get_heartbeat())
    pprint(api.get_venue_heartbeat(VENUE))
    pprint(api.get_stocks(VENUE))
    pprint(api.get_stocks(VENUE)["symbols"][0]["symbol"])
    pprint(api.get_quote(VENUE, STOCK))


def get_accounts():
    """
    From the API docs for DELETE orders: https://starfighter.readme.io/docs/cancel-an-order
    The 401 Unauthorized request will return the account of the order in the request
    {
      "ok": false,
      "error": "Not authorized to delete that order.  You have to own account ABC123456."
    }
    So go through all orders (since they are increasing integer ids) and assemble a set of accounts
    """
    accounts = set([])
    for i in range(1, 500):
        response = requests.delete("https://api.stockfighter.io/ob/api/venues/{0}/stocks/{1}/orders/{2}"
                                   .format(VENUE, STOCK, i),
                                   headers=api.API_HEADERS)
        json = response.json()
        m = re.search('account (.*).', json["error"])
        account = m.group(1)
        accounts.add(account)
    return accounts


def log_executions(account):
    """
    API docs say that websocket feeds are not authorized: https://starfighter.readme.io/docs/quotes-ticker-tape-websocket
    So using the gathered account names can see the executions in the market
    """
    pprint("Starting to log executions for {0}...".format(account))

    def on_message(ws, message):
        execution = json.loads(message)
        EXECUTIONS[account] += [execution]
        pprint(execution)

    def on_error(ws, error):
        pprint(error)

    def on_close(ws):
        pprint("### Closed Websocket For {0} ###".format(account))

    def on_open(ws):
        def run(*args):
            EXECUTIONS[account] = []
            time.sleep(1)
            pprint("### Opening Websocket For {0} ###".format(account))
        thread.start_new_thread(run, ())

    def connect_to_executions_feed(trading_account, venue, stock=None):
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

    thread.start_new_thread(connect_to_executions_feed, (account, VENUE, STOCK))
    # connect_to_executions_feed(account, VENUE, STOCK)
    pprint("Execution logging for {0} started...".format(account))


def log_quotes(account):
    """
    API docs say that websocket feeds are not authorized: https://starfighter.readme.io/docs/quotes-ticker-tape-websocket
    So using the gathered account names can see the executions in the market
    """
    pprint("Starting to log quotes for {0}...".format(account))

    def on_message(ws, message):
        quote = json.loads(message)["quote"]
        QUOTES.append(quote)

    def on_error(ws, error):
        pprint(error)

    def on_close(ws):
        pprint("### Closed Websocket For {0} ###".format(account))

    def on_open(ws):
        def run(*args):
            time.sleep(1)
            pprint("### Opening Websocket For {0} ###".format(account))
        thread.start_new_thread(run, ())

    def connect_to_quotes_feed(trading_account, venue, stock=None):
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

    thread.start_new_thread(connect_to_quotes_feed, (account, VENUE, STOCK))
    pprint("Quotes logging for {0} started...".format(account))


def submit_evidence(account, explanation_link, executive_summary, instance_id):
    explanation_link = "https://github.com/gstaff/stockfighter"
    executive_summary = "First identified 100 accounts on exchange via error status on attempted order deletes." \
                        "Next got list of executions for all accounts via the executions websocket feed." \
                        "Also tracked quotes over the same timespan via the quotes websocket feed." \
                        "Noticed that 72 accounts only sumbitted market orders in small quantities." \
                        "These are retail investors." \
                        "The other 28 accounts only used limit orders." \
                        "These are market makers." \
                        "Using the execution history to calculate a P&L value for all accounts revealed some trends." \
                        "None of the retail investors had significant gains or losses." \
                        "Market makers had much more significant P&L, positive and negative." \
                        "One account stood out as an outlier for its significant losses; twice as much as the next."
    evidence = {
        "account": account,
        "explanation_link": explanation_link,
        "executive_summary": executive_summary
    }
    response = requests.post("https://www.stockfighter.io/gm/instances/{0}/judge".format(instance_id))
    # post to /gm/instances/YOUR_INSTANCE_ID/judge


def main():
    check_api()
    if os.path.exists("accounts.json"):
        with open("accounts.json") as data:
            accounts = json.load(data)
    else:
        accounts = get_accounts()
    pprint(accounts)
    with open("accounts.txt", "w") as outfile:
        pprint(accounts, stream=outfile)
    with open("accounts.json", "wb") as outfile:
        json.dump(list(accounts), outfile)
    log_quotes(ACCOUNT)
    for account in accounts:
        log_executions(account)
    time.sleep(60 * 10)
    for account in accounts:
        with open("/home/grant/PycharmProjects/stockfighter/executions/{0}_executions.json".format(account), "w") as outfile:
            json.dump(EXECUTIONS[account], outfile)
    with open("/home/grant/PycharmProjects/stockfighter/quotes.json", "w") as outfile:
        json.dump(QUOTES, outfile)


if __name__ == '__main__':
    main()
