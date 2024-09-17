import pandas as pd
from db import weather_collection


def celsius_to_fahrenheit(celsius):
    return (celsius * 9 / 5) + 32


def calculate_heat_index(temp_f, humidity):
    c1 = -42.379
    c2 = 2.04901523
    c3 = 10.14333127
    c4 = -0.22475541
    c5 = -0.00683783
    c6 = -0.05481717
    c7 = 0.00122874
    c8 = 0.00085282
    c9 = -0.00000199

    hi = (c1 + (c2 * temp_f) + (c3 * humidity) + (c4 * temp_f * humidity) +
          (c5 * temp_f ** 2) + (c6 * humidity ** 2) +
          (c7 * temp_f ** 2 * humidity) + (c8 * temp_f * humidity ** 2) +
          (c9 * temp_f ** 2 * humidity ** 2))
    return hi



def fill_missing_heat_index(row):
    if pd.isna(row['_heatindexm']):
        temp_f = celsius_to_fahrenheit(row['_tempm'])
        # Calculate heat index if temperature and humidity exist
        if row['_hum'] is not None:
            return calculate_heat_index(temp_f, row['_hum'])
    return row['_heatindexm']


def transform_data():
    file_path = 'weather_data.csv'
    df = pd.read_csv(file_path)

    # print(df.head())

    # print(df.info())

    print(df.isnull().sum())
    df.rename(columns=lambda x: x.strip(), inplace=True)

    df['_tempm'] = df['_tempm'].fillna(df['_tempm'].mean())
    df['_hum'] = df['_hum'].fillna(method='ffill')
    df['_pressurem'] = df['_pressurem'].fillna(method='ffill')
    df['_heatindexm'] = df.apply(fill_missing_heat_index, axis=1)
    df.drop(df[df['_pressurem'] <= 0 ].index, inplace=True)
    df_cleaned = df.drop_duplicates(subset=['datetime_utc', '_tempm', '_hum', '_pressurem'], keep='first')

    df_cleaned['datetime_utc'] = pd.to_datetime(df_cleaned['datetime_utc'])

    df_grouped = df_cleaned.groupby('datetime_utc').agg({
        '_tempm': ['min', 'max', 'mean'],
        '_hum': 'mean',
        '_pressurem': 'mean',
        '_heatindexm': 'mean'
    })

    df_grouped.columns = ['temp_min', 'temp_max', 'temp_avg', 'humidity_avg', 'pressure_avg', 'heat_index_avg']

    df_grouped.reset_index(inplace=True)

    weather_data = df_grouped.to_dict(orient='records')

    # print(len(weather_data))

    weather_collection.delete_many({})
    weather_collection.create_index({"datetime_utc": 1})

    weather_collection.insert_many(weather_data)
