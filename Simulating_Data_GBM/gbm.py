# Imports
# Standard libraries
import os
import random
import string
# Local libraries
import click
import numpy as np
import pandas as pd

class GBMAssetSimulator:
    """
    Generates OHLCV with GBM for pricing and Patreo distribution for volatility.
    Outputs 5 CSV files when called containing data between two inclusive dates.
    Pricing and volume data is uncorrelated in this model.
    """
    def __init__(
        self,
        start_date,
        end_date,
        output_dir,
        symbol_length,
        init_price,
        mu,
        sigma,
        pareto_shape
    ):
        self.start_date=start_date
        self.end_date=end_date
        self.output_dir=output_dir
        self.symbol_length=symbol_length
        self.init_price=init_price
        self.mu=mu
        self.sigma=sigma
        self.pareto_shape=pareto_shape

    def _generate_ticker(self):
        return ''.join(
            random.choices(                             # Concatenates random uppercase letters to form a ticker
                string.ascii_uppercase,
                k=self.symbol_length
            )
        )
    
    def _create_df(self):
        dates=pd.date_range(                            # Creates the dataframe based on the time frame and number of intervals
            self.start_date,
            self.end_date,
            freq='B'
        )
        zeros = pd.Series(np.zeros(len(dates)))
        return pd.DataFrame(
            {
            'date':dates,                               # Dictionary that maps columns to data
            'open':zeros,
            'high':zeros,
            'low':zeros,
            'close':zeros,
            'volume':zeros
            }
        )[['date','open','high','low','close','volume']]
    
    def _generate_GBM(self,data):
        n = len(data)
        T = n/252                                       # Years
        dt = T/(4*n)                                    # Factor of 4 as there are 4 data points required each day
        asset_path = np.exp(
            (self.mu - self.sigma**2/2)*dt + self.sigma*np.random.normal(0, np.sqrt(dt), size=(4*n))
        )
        return self.init_price*asset_path.cumprod()     # Determines price for the given timestep
    
    def _adjust_append_price_data(self,data,path):
        data['open'] = path[0::4]                       # Open data is given every 4 points
        data['close'] = path[3::4]                      # Close data is given every 4 points offset by 3
        data['high'] = np.maximum(                      # High data is the max of all 4 data points in a day
            np.maximum(path[0::4], path[1::4]),
            np.maximum(path[2::4], path[3::4])
        )
        data['low'] = np.minimum(                       # Low data is the min of all 4 data points in a day
            np.minimum(path[0::4], path[1::4]),
            np.minimum(path[2::4], path[3::4])
        )
    
    def _append_volume_data(self,data):
        data['volume'] = np.array(
            list(
                map(
                    int,
                    np.random.pareto(
                        self.pareto_shape,              # Generates random volume data from the pareto distribution
                        size=len(data)
                    )
            )
        )
        )

    def _output_dataframe(self,symbol,data):
        output_file = os.path.join(self.output_dir, '%s.csv' % symbol)
        data.to_csv(output_file, index=False, float_format='%.2f')

    def __call__(self):
        symbol = self._generate_ticker()
        data = self._create_df()
        path = self._generate_GBM(data)
        self._adjust_append_price_data(data,path)
        self._append_volume_data(data)
        self._output_dataframe(symbol,data)

@click.command()
@click.option('--num-assets', 'num_assets', default='1', help='Number of separate assets to generate files for')
@click.option('--random-seed', 'random_seed', default='42', help='Random seed to set for both Python and NumPy for reproducibility')
@click.option('--start-date', 'start_date', default=None, help='The starting date for generating the synthetic data in YYYY-MM-DD format')
@click.option('--end-date', 'end_date', default=None, help='The starting date for generating the synthetic data in YYYY-MM-DD format')
@click.option('--output-dir', 'output_dir', default=None, help='The location to output the synthetic data CSV file to')
@click.option('--symbol-length', 'symbol_length', default='5', help='The length of the asset symbol using uppercase ASCII characters')
@click.option('--init-price', 'init_price', default='100.0', help='The initial stock price to use')
@click.option('--mu', 'mu', default='0.1', help=r"The drift parameter, \mu for the GBM SDE")
@click.option('--sigma', 'sigma', default='0.3', help=r"The volatility parameter, \sigma for the GBM SDE")
@click.option('--pareto-shape', 'pareto_shape', default='1.5', help='The shape of the Pareto distribution simulating the trading volume')

def cli(num_assets, random_seed, start_date, end_date, output_dir, symbol_length, init_price, mu, sigma, pareto_shape):
    num_assets = int(num_assets)
    random_seed = int(random_seed)
    symbol_length = int(symbol_length)
    init_price = float(init_price)
    mu = float(mu)
    sigma = float(sigma)
    pareto_shape = float(pareto_shape)

    random.seed(random_seed)
    np.random.seed(seed=random_seed)

    gbmas = GBMAssetSimulator(
        start_date,
        end_date,
        output_dir,
        symbol_length,
        init_price,
        mu,
        sigma,
        pareto_shape
    )

    for i in range(num_assets):
        print('Generating asset path %d of %d...' % (i+1, num_assets))
        gbmas()

if __name__ == "__main__":                              # Allows GBM.py to be both a CLI tool and Library
    cli()                                               # Will not run if added to another notebook or script unless specifically requested in the terminal.