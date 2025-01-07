import pandas as pd
import geopandas as gpd
from consts import raw_files_dir, processed_socio_dir, socio_vars


def build_ct_socio_data(file_name):
    
    #### Population
    ct_population_file = f"{raw_files_dir}/sociodemographic/ct_total_population/ACSDT5Y2023.B01003-Data.csv"
    ct_pop_df = pd.read_csv(ct_population_file, skiprows=[1])

    ct_pop_df["GEO_ID"] = ct_pop_df["GEO_ID"].str.replace("1400000US", "", regex=False)
    ct_pop_df = ct_pop_df[["GEO_ID", "B01003_001E"]]
    
    #### Race
    ct_race_file = f"{raw_files_dir}/sociodemographic/ct_race_hispanic_not_hispanic/DECENNIALDHC2020.P9-Data.csv"
    ct_race_df = pd.read_csv(ct_race_file, skiprows=[1])
    ct_race_df["GEO_ID"] = ct_race_df["GEO_ID"].str.replace("1400000US", "", regex=False)
    
    ct_race_df = ct_race_df[["GEO_ID", "P9_002N", "P9_003N", "P9_005N", "P9_006N", "P9_007N", "P9_008N", "P9_009N",	"P9_010N" ]]

    #### Merge
    merged_df = pd.merge(ct_pop_df, ct_race_df, on="GEO_ID", how="inner")
    merged_df.rename(columns={"GEO_ID": "GEOID"}, inplace=True)


    #### Save as feather
    feather_file = f"{processed_socio_dir}/{file_name}.feather"
    merged_df.to_feather(feather_file)

    print(f"CT Population data successfully saved to Feather: {feather_file}")

def read_feather(file_name, id):
    feather_file = f"{processed_socio_dir}/{file_name}.feather"
    df = pd.read_feather(feather_file)
    ct = df[df["GEOID"] == id]

    result = [
        {"name": description, "value": ct[var].iloc[0] if not ct.empty else None}
        for var_dict in socio_vars
        for var, description in var_dict.items()
    ]

    print(ct)
    print(result)

    
if __name__ == "__main__":
    # build_ct_socio_data("ct_socio")
    read_feather("ct_socio", "17001000201")