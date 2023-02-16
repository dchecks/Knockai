import pandas as pd
from sklearn.linear_model import LinearRegression

from knockai.log_decode import log_decode

# Load the data into a Pandas DataFrame
# df = log_decode("resources/runs/r02/r2-100k-af.txt")

def injpw_af_regression(df):
    # Cut down the datafram to just the columns needed
    df = df[["Secs", "INJ_PW", "WB_Oxy"]]

    # Split the data into features (INJ_PW) and target (WB_Oxy)
    X = df["INJ_PW"].values.reshape(-1, 1)
    y = df["WB_Oxy"].values.reshape(-1, 1)

    # Fit the linear regression model to the data
    reg = LinearRegression().fit(X, y)

    # Get the coefficient and intercept of the regression line
    coef = reg.coef_[0][0]
    intercept = reg.intercept_[0]

    # The regression line can be represented as y = ax + b, where a = coefficient and b = intercept
    print("y = {:.2f}x + {:.2f}".format(coef, intercept))

    return coef, intercept
