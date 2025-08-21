import matplotlib.pyplot as plt
import pandas as pd
import os

folder = '/Users/thomasfish/Desktop/Quant_Prep/Independent_Projects/GBM_Sim/GBMSimOutput'
tickers = []
for fname in os.listdir(folder):
    if fname.lower().endswith('.csv'):
        ticker, extension = os.path.splitext(fname)
        tickers.append(ticker)

if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(15,5))
    for i in range(len(tickers)):
        ticker = tickers[i]
        df = pd.read_csv(f'/Users/thomasfish/Desktop/Quant_Prep/Independent_Projects/GBM_Sim/GBMSimOutput/{ticker}.csv')
        df['date'] = pd.to_datetime(df['date'], format="%Y-%m-%d")
        df.plot(ax=ax, linewidth=0.2, x='date', y=["open","high","low","close"], legend=False)
    plt.title("Monte-Carlo Simulation of Feasible Stock Price Paths")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.tight_layout()
    plt.show()