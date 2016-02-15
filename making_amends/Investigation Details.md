# Investigation Details

### Summary
- After gathering execution data for all accounts trading TSI on EUQDEX it appears that account RMB73022728 may be using insider trading to earn outsize profits on relatively low trading volume.

### Gathering Data for Analysis
- The Stockfighter API for deleting orders returns the account owning an order upon an unauthorized request.
- Using this to scan the first 500 orders I was able to assemble a set of 100 accounts trading the stock of interest.
- The Stockfighter executions websocket feed does not apply authorization.
- Spinning up a connection for each of the accounts and gathering a list of all executions for 5 minutes provided a dataset for finding the suspect.
- Code can be found in making_amends.py
- Data can be found in accounts.json, accounts.txt, and the excutions directory

### Analyzing the Data
- With a history of executions for all accounts the next step was to classify the accounts.
- It immediately stood out that accounts could be classified by order type.
  - Retail investors only used market orders in small quantities (under 100).
  - Professional investors only used limit orders with larger quantities.
  - There were 72 retail accounts and 28 professional accounts.
- Aggregating over the closed orders of all accounts I looked at two key metrics: trading volume and P&L.
  - The retail accounts could be excluded from the investigation right away as the amount of money involved in their trades was immaterial
  - Of the remaining institutional accounts the trading volume metric indicated another distinction.
    - There were 25 smaller institutions with similar volumes (14k - 20k total volume over the interval).
    - There were 3 larger institutions with an order of magnitude more trading volume than the smaller players (126k+ total volume over the interval).
  - Insider trading would be pointless unless there were extra profit to be gained so I ordered the institutional accounts by P&L.
    - The most profitable account was one of the smaller institutions which is not a red flag by itself. However:
      - The P&L for this account was 37% higher than the next highest account.
      - The total trading volume for this account was only 83% of the next *lowest* institutional account.
      - The combination of these factors is anomalous as P&L correlates strongly with trading volume for market making strategies (R^2 of 0.71 among the 25 smaller accounts here).
- Code can be found in analysis.py
- Data can be found in suspects.csv

### Conclusion
- The combination of high P&L and low trading volume for RMB73022728 is enough of an outlier to justify an investigation for insider trading.
