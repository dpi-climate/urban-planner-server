import pandas as pd

def default():
    # Load the Feather file
    feather_file = "./files/Illinois_prcp_risks_round.feather"
    df = pd.read_feather(feather_file)

    # Display the first few rows to understand the structure of the data
    print("Data Preview:")
    print(df.head())

    # List all the column names (properties)
    print("\nProperties (Columns) in the DataFrame:")
    print(df.columns.tolist())

    # Extract specific properties (e.g., 'property_name1', 'property_name2')
    # Replace 'property_name1', 'property_name2' with the actual column names
    properties_of_interest = ['property_name1', 'property_name2']
    if all(prop in df.columns for prop in properties_of_interest):
        extracted_data = df[properties_of_interest]
        print("\nExtracted Properties:")
        print(extracted_data.head())
    else:
        print("\nOne or more specified properties do not exist in the data.")

def get_props():
    # Load the Feather file
    feather_file = "./files/Illinois_prcp_risks_round.feather"
    df = pd.read_feather(feather_file)

    properties_of_interest = ['1980', 'risk_2yr (', 'risk_5yr (', 'risk_10yr', 'risk_25yr', 'risk_50yr', 'risk_100yr', 'risk_200yr', 'risk_500yr']
    index_to_extract = 18742

    if index_to_extract in df.index:
        # Extract the properties for the specified index
        extracted_row = df.loc[index_to_extract, properties_of_interest]
        print(f"Extracted properties for index {index_to_extract}:")
        print(extracted_row)
        
        formatted_data = [{"year": column, "value": value} for column, value in extracted_row.items()]

        print(f"Formatted data for index {index_to_extract}:")
        print(formatted_data)

    else:
        print(f"Index {index_to_extract} does not exist in the DataFrame.")

# default()
print("#####")
get_props()