# libraries

# flask tools
from flask import Flask, jsonify, request, send_file

# data / stats tools
import pandas as pd
import numpy as np
import statsmodels.api as sm
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import zscore

# needed to encode plot as bytes
import io

from pandas.plotting import register_matplotlib_converters

# define helper functions
# load data
def load_data():
    df = pd.read_csv("data/housing_in_london_monthly_variables.csv")
    df['date'] = pd.to_datetime(df['date'], format="%Y-%m-%d")
    return df


# log transform to array for statmodels
def transform_data(df, var):
    y = df[var].apply(lambda x: np.log(1 + x))
    y = y.reset_index(drop=True)
    y = y.astype(float)
    return np.array(y)


# function to create ts plot for prices / sales
def ts_plot(df, area):
    plot_df = df[['date', 'area', 'average_price', 'houses_sold']]
    plot_df.loc[:,'average_price'] = zscore(plot_df['average_price'], nan_policy='omit')
    plot_df.loc[:,'houses_sold'] = zscore(plot_df['houses_sold'], nan_policy='omit')
    plot_df = plot_df[plot_df.area == area].melt(['area', 'date'])
    plot_df = plot_df.drop('area', axis=1)
    sns.lineplot(x="date", y="value", hue="variable", data=plot_df)
    register_matplotlib_converters()

    # save plot as bytes to return to api
    bytes_image = io.BytesIO()
    plt.savefig(bytes_image, format='png')
    bytes_image.seek(0)
    return bytes_image


# filter data for given area
def model_data(df, area):
    return df.loc[
        df.area == area,
        ['date','average_price','houses_sold']
    ]


# fit ela model
def ela_model(df):
    df = df.fillna(method="ffill")
    df = df.dropna().set_index("date")
    X = transform_data(df, "average_price")
    y = transform_data(df, "houses_sold")
    X = sm.add_constant(X)
    ela_model = sm.OLS(endog=y, exog=X)
    res = ela_model.fit()
    return res


# return results in dataframe
def return_results(df, area):
    model_df = model_data(df, area)
    res = ela_model(model_df)
    res_df = pd.DataFrame()
    res_df['var'] = ['Intercept','log(Price)']
    res_df['coef'] = res.params
    res_df['pvalue'] = res.pvalues
    return res_df


# load data into session
housing_monthly = load_data()

# get unique areas
# areas = list(housing_monthly.area.unique())

# initialize app
app = Flask(__name__)

# get latest average price by area
@app.route('/price', methods=['GET','POST'])
def get_latest_avg_price():

    area = request.get_json().get('area')

    df=housing_monthly[
        (housing_monthly.date == max(housing_monthly.date)) &
        (housing_monthly.area == area)
    ].reset_index(drop=True)

    price = {
        'date': str(df.date[0]),
        'area': area,
        'area code': str(df.code[0]),
        'average price': str(df.average_price[0]),
        'number of crimes': str(df.no_of_crimes[0])
    }

    return jsonify(price)

# get price ela for area
@app.route('/ela', methods=['GET','POST'])
def get_ela():
    
    area = request.get_json().get('area')
    results = return_results(housing_monthly, area)
    
    return results.to_json(orient = "records")

# return plot of two normalized time series
@app.route('/plot', methods=['GET','POST'])
def get_ts_plot():

    area = request.get_json().get('area')
    bytes_obj = ts_plot(housing_monthly, area)

    return send_file(bytes_obj,
                     attachment_filename='plot.png',
                     mimetype='image/png')


if __name__ == "__main__":
    app.run(debug=True)