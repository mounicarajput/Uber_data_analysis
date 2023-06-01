import pandas as pd

# Define the path to the input and output CSV files
input_csv_path = "/Users/monikarajput/Documents/personal_project/uber_analysis/uber_data.csv"
output_csv_path = "/Users/monikarajput/Documents/personal_project/uber_analysis/output/"

# Step 1: Extract - Load data from CSV
def extract_data(csv_path):
    df = pd.read_csv(csv_path)
    return df

# Step 2: Transform - Apply transformation function

def transform(df, *args, **kwargs):
    """
    Template code for a transformer block.

    Add more parameters to this function if this block has multiple parent blocks.
    There should be one parameter for each output variable from each parent block.

    Args:
        data: The output from the upstream parent block
        args: The output from any additional upstream blocks (if applicable)

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """
    # Specify your transformation logic here
    df["tpep_pickup_datetime"] = pd.to_datetime(df["tpep_pickup_datetime"])
    df["tpep_dropoff_datetime"] = pd.to_datetime(df["tpep_dropoff_datetime"])
    df = df.drop_duplicates().reset_index(drop=True)
    df['trip_id'] = df.index
    datetime_dim = df[['tpep_pickup_datetime', 'tpep_dropoff_datetime']].reset_index(drop=True)
    datetime_dim['tpep_pickup_datetime'] = datetime_dim['tpep_pickup_datetime']
    datetime_dim['pickup_hour'] = datetime_dim['tpep_pickup_datetime'].dt.hour
    datetime_dim['pickup_day'] = datetime_dim['tpep_pickup_datetime'].dt.day
    datetime_dim['pickup_month'] = datetime_dim['tpep_pickup_datetime'].dt.month
    datetime_dim['pickup_year'] = datetime_dim['tpep_pickup_datetime'].dt.year
    datetime_dim['pickup_weekday'] = datetime_dim['tpep_pickup_datetime'].dt.weekday

    datetime_dim['tpep_dropoff_datetime'] = datetime_dim['tpep_dropoff_datetime']
    datetime_dim['drop_hour'] = datetime_dim['tpep_pickup_datetime'].dt.hour
    datetime_dim['drop_day'] = datetime_dim['tpep_pickup_datetime'].dt.day
    datetime_dim['drop_month'] = datetime_dim['tpep_pickup_datetime'].dt.month
    datetime_dim['drop_year'] = datetime_dim['tpep_pickup_datetime'].dt.year
    datetime_dim['drop_weekday'] = datetime_dim['tpep_pickup_datetime'].dt.weekday
    datetime_dim['datetime_id'] = datetime_dim.index
    datetime_dim = datetime_dim[
        ['datetime_id', 'tpep_pickup_datetime', 'pickup_hour', 'pickup_day', 'pickup_month', 'pickup_year',
         'pickup_weekday', 'tpep_dropoff_datetime', 'drop_hour', 'drop_day', 'drop_month', 'drop_year', 'drop_weekday']]

    passenger_count_dim = df[['passenger_count']]
    passenger_count_dim['passenger_count_id'] = passenger_count_dim.index
    passenger_count_dim = passenger_count_dim[['passenger_count_id', 'passenger_count']]

    trip_distance_dim = df[['trip_distance']].reset_index(drop=True)
    trip_distance_dim['trip_distance_id'] = trip_distance_dim.index
    trip_distance_dim = trip_distance_dim[['trip_distance_id', 'trip_distance']]

    rate_code_type = {
        1: "Standard rate",
        2: "JFK",
        3: "Newark",
        4: "Nassau or Westchester",
        5: "Negotiated fare",
        6: "Group ride"}

    rate_code_dim = df[['RatecodeID']]
    rate_code_dim['rate_code_id'] = df.index
    rate_code_dim['rate_code_name'] = rate_code_dim['RatecodeID'].map(rate_code_type)
    rate_code_dim = rate_code_dim[['rate_code_id', 'RatecodeID', 'rate_code_name']]

    pickup_location_dim = df[['pickup_longitude', 'pickup_latitude']]
    pickup_location_dim['pickup_location_id'] = pickup_location_dim.index
    pickup_location_dim = pickup_location_dim[['pickup_location_id', 'pickup_longitude', 'pickup_latitude']]

    drop_location_dim = df[['dropoff_longitude', 'dropoff_latitude']]
    drop_location_dim['drop_location_id'] = drop_location_dim.index
    drop_location_dim = drop_location_dim[['drop_location_id', 'dropoff_longitude', 'dropoff_latitude']]

    payment_type_name = {
        1: "Credit card",
        2: "Cash",
        3: "No charge",
        4: "Dispute",
        5: "Unknown",
        6: "Voided trip"}

    payment_type_dim = df[['payment_type']]
    payment_type_dim['payment_type_id'] = payment_type_dim.index
    payment_type_dim['payment_type_name'] = payment_type_dim['payment_type'].map(payment_type_name)
    payment_type_dim = payment_type_dim[['payment_type_id', 'payment_type', 'payment_type_name']]

    fact_table = df.merge(passenger_count_dim, left_on='trip_id', right_on='passenger_count_id') \
        .merge(trip_distance_dim, left_on='trip_id', right_on='trip_distance_id') \
        .merge(rate_code_dim, left_on='trip_id', right_on='rate_code_id') \
        .merge(pickup_location_dim, left_on='trip_id', right_on='pickup_location_id') \
        .merge(drop_location_dim, left_on='trip_id', right_on='drop_location_id') \
        .merge(datetime_dim, left_on='trip_id', right_on='datetime_id') \
        .merge(payment_type_dim, left_on='trip_id', right_on='payment_type_id') \
        [['trip_id', 'VendorID', 'datetime_id', 'passenger_count_id',
          'trip_distance_id', 'rate_code_id', 'store_and_fwd_flag', 'pickup_location_id', 'drop_location_id',
          'payment_type_id', 'fare_amount', 'extra', 'mta_tax', 'tip_amount', 'tolls_amount',
          'improvement_surcharge', 'total_amount']]

    return {
        'datetime_dim': datetime_dim,
        'passenger_count_dim': passenger_count_dim,
        'trip_distance_dim': trip_distance_dim,
        'rate_code_dim': rate_code_dim,
        'pickup_location_dim': pickup_location_dim,
        'drop_location_dim': drop_location_dim,
        'payment_type_dim': payment_type_dim,
        'fact_table': fact_table
    }

# Step 3: Load - Save transformed data to CSV
def load_data(dataframes, output_dir):
    for name, df in dataframes.items():
        csv_path = output_dir + '/' + name + '.csv'
        df.to_csv(csv_path, index=False)

# Run the pipeline
if __name__ == "__main__":
    # Step 1: Extract - Load data from CSV
    extracted_data = extract_data(input_csv_path)

    # Step 2: Transform - Apply transformation function
    transformed_data = transform(extracted_data)

    # Step 3: Load - Save transformed data to CSV
    load_data(transformed_data, output_csv_path)

