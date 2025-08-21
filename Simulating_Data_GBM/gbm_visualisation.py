import matplotlib.pyplot as plt
import pandas as pd
import os

folder = '/Users/thomasfish/Desktop/Quant_Prep/Independent_Projects/GBM_Sim/GBMSimOutput'
tickers = []
for fname in os.listdir(folder):
    if fname.lower().endswith('.csv'):
        ticker, ext = os.path.splitext(fname)
        tickers.append(ticker)

if __name__ == "__main__":
    fig, axs = plt.subplots(3, 1, figsize=(15,15))
    for i in range(3):
        ticker = tickers[i]
        df = pd.read_csv(f'/Users/thomasfish/Desktop/Quant_Prep/Independent_Projects/GBM_Sim/GBMSimOutput/{ticker}.csv')
        df['date'] = pd.to_datetime(df['date'], format="%Y-%m-%d")
        if i == 0:
            df.plot(ax=axs[i], x='date', y=["open","high","low","close","volume"], linewidth=1, sharex=True)
        else:
            df.plot(ax=axs[i], x='date', y=["open","high","low","close","volume"], linewidth=1, sharex=True, legend=False)
    plt.title("3 Examples of Stochastic Price Data")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.tight_layout()
    plt.show()
