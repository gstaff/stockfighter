import csv
import json
from pprint import pprint

LAST_PRICE = 10984

with open("accounts.json", "r") as accounts_file:
    accounts = json.load(accounts_file)
    with open("scratch.csv", "w") as outfile:
        fieldnames = ['account', 'totalFilled', 'pnl']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for account in accounts:
            total_filled = 0
            cash = 0
            position = 0
            with open("/home/grant/PycharmProjects/stockfighter/executions/{0}_executions.json".format(account), "r") as executions_file:
                executions = json.load(executions_file)
                for execution in executions:
                    total_filled += execution["filled"]
                    order = execution["order"]
                    order_open = order["open"]
                    if not order_open:
                        direction = order["direction"]
                        fills = order["fills"]
                        for fill in fills:
                            qty = fill["qty"]
                            price = fill["price"]
                            if direction == "buy":
                                cash -= qty * price
                                position += qty
                            elif direction == "sell":
                                cash += qty * price
                                position -= qty
                pnl = cash + position * LAST_PRICE
                pprint("{0} {1} {2}".format(account, total_filled, pnl))
                writer.writerow({"account": account, "totalFilled": total_filled, 'pnl': pnl})
