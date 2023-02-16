# Converts a tab separated log file into a dataframe, having the following columns:
#Secs	RPM	MAP	ETemp	IAT	VOLTS	TPS	OXY	WB_Oxy	INJ_PW	INJ_DC	Boost_	WG_DC	ISC_DC	Zone	Ign_Adv	SCE	MAPLim	RPMLim	Accel_	RadFan	Aux1	Aux1	Orun_Vac	Iat_Rtd	Stagin	IDLEST	TPSCls	Markers	;"

import pandas as pd

def log_decode(log_file):
    # Skip the first 3 lines
    df = pd.read_csv(log_file, sep='\t', skiprows=3)
    # Drop the last column
    df = df.drop(df.columns[-1], axis=1)
    df.columns = ['Secs', 'RPM', 'MAP', 'ETemp', 'IAT', 'VOLTS', 'TPS', 'OXY', 'WB_Oxy', 'INJ_PW', 'INJ_DC', 'Boost_', 'WG_DC', 'ISC_DC', 'Zone', 'Ign_Adv', 'SCE', 'MAPLim', 'RPMLim', 'Accel_',
                  'RadFan', 'Aux1', 'Aux1', 'Orun_Vac', 'Iat_Rtd', 'Stagin', 'IDLEST', 'TPSCls', 'Markers']
    return df


def clean_data(df):
    # Remove WB_Oxy values greater than 15 as these are likely injector shut-off
    df = df[df["WB_Oxy"] < 15]
    # Remove Accel_ active values
    df = df[df["Accel_"] == 'Off']

    return df

if __name__ == '__main__':
    df = log_decode('resources/runs/r02/r2-100k-af.txt')
    # Print all columns
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 300)
    # Set the print width
    print(df.head(50))
