from data_loader import load_json_data
from loc_access import LocDataAccess
from similarity_search import perform_similarity_search, find_similar_passengers, parse_xml
from locationSimilarity import haversine, location_similarity_score, location_matching, address_str_similarity_score
from ageSimilarity import age_similarity_score, calculate_age
from obstructor import introduce_dob_typos, introduce_error_airport, introduce_error_nat_city, introduce_error_sex, introduce_typos, update_loc_airport
from base_similarity import count_likelihood2, string_similarity
from TrainTest import run_xgboost_classification_v2

import pandas as pd
import dask.dataframe as dd
from sklearn.metrics import confusion_matrix, matthews_corrcoef
from sklearn.metrics import classification_report, roc_auc_score, auc, precision_recall_curve
import seaborn as sns
import matplotlib.pyplot as plt
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from xgboost import plot_importance

import numpy as np
import os
import glob
from collections import defaultdict
from fuzzywuzzy import fuzz
import string
from concurrent.futures import ProcessPoolExecutor
from random import random, choice, choices, randint
from datetime import datetime, timedelta

airport_data_access = LocDataAccess.get_instance()  # Access the singleton instance
df = pd.read_csv('parsed_xml.csv')
geocrosswalk = pd.read_csv('data/geoCrosswalk/GeoCrossWalkMed.csv')
print(pd.__version__)


def standardize_mark(mark):
    """
    Standardize the mark by sorting the parts of the mark.
    For example, 'Obs1-Obs3' and 'Obs3-Obs1' would both become 'Obs1-Obs3'.
    """
    parts = mark.split('-')
    parts_sorted = sorted(parts)
    standardized_mark = '-'.join(parts_sorted)
    return standardized_mark


n = 1100
df_obstruct1 = df.head(n).copy()
rate = 0.3
rate_typos = 0.2
df_obstruct1['Sex'] = df_obstruct1.apply(introduce_error_sex, args = (0.025, ), axis = 1)
df_obstruct1['Firstname'] = df_obstruct1['Firstname'].apply(lambda x: introduce_typos(x, rate_typos))
df_obstruct1['Surname'] = df_obstruct1['Surname'].apply(lambda x: introduce_typos(x, rate_typos))
df_obstruct1['Address'] = df_obstruct1['Address'].apply(lambda x: introduce_typos(x, rate_typos))
df_obstruct1['DOB'] = df_obstruct1['DOB'].apply(lambda x: introduce_dob_typos(x, rate_typos))
df_obstruct1['OriginIATA'] = df_obstruct1.apply(lambda row: introduce_error_airport(row, 'OriginIATA', geocrosswalk, 'city', rate), axis=1)
df_obstruct1['DestinationIATA'] = df_obstruct1.apply(lambda row: introduce_error_airport(row, 'DestinationIATA', geocrosswalk, 'city', rate), axis=1)
df_obstruct1['Nationality'] = df_obstruct1.apply(introduce_error_nat_city, args = (geocrosswalk, 'Nationality', 'HH_ISO', rate), axis = 1)
df_obstruct1['CityName'] = df_obstruct1.apply(introduce_error_nat_city, args = (geocrosswalk, 'CityName', 'City', rate), axis = 1)
df_obstruct1[['OriginLat', 'OriginLon', 'OriginCity', 'OriginCountry']] = df_obstruct1.apply(update_loc_airport, args = ('OriginIATA', ), axis = 1)
df_obstruct1[['DestinationLat', 'DestinationLon', 'DestinationCity', 'DestinationCountry']] = df_obstruct1.apply(update_loc_airport, args = ('DestinationIATA', ), axis = 1)

df_obstruct2 = df.head(n).copy()
rate = 0.5
rate_typos = 0.3
df_obstruct2['Sex'] = df_obstruct2.apply(introduce_error_sex, args = (0.05, ), axis = 1)
df_obstruct2['Firstname'] = df_obstruct2['Firstname'].apply(lambda x: introduce_typos(x, rate))
df_obstruct2['Surname'] = df_obstruct2['Surname'].apply(lambda x: introduce_typos(x, rate))
df_obstruct2['Address'] = df_obstruct2['Address'].apply(lambda x: introduce_typos(x, rate))
df_obstruct2['DOB'] = df_obstruct2['DOB'].apply(lambda x: introduce_dob_typos(x, rate))
df_obstruct2['OriginIATA'] = df_obstruct2.apply(lambda row: introduce_error_airport(row, 'OriginIATA', geocrosswalk, 'city', rate), axis=1)
df_obstruct2['DestinationIATA'] = df_obstruct2.apply(lambda row: introduce_error_airport(row, 'DestinationIATA', geocrosswalk, 'city', rate), axis=1)
df_obstruct2['Nationality'] = df_obstruct2.apply(introduce_error_nat_city, args = (geocrosswalk, 'Nationality', 'HH_ISO', rate), axis = 1)
df_obstruct2['CityName'] = df_obstruct2.apply(introduce_error_nat_city, args = (geocrosswalk, 'CityName', 'City', rate), axis = 1)
df_obstruct2[['OriginLat', 'OriginLon', 'OriginCity', 'OriginCountry']] = df_obstruct2.apply(update_loc_airport, args = ('OriginIATA', ), axis = 1)
df_obstruct2[['DestinationLat', 'DestinationLon', 'DestinationCity', 'DestinationCountry']] = df_obstruct2.apply(update_loc_airport, args = ('DestinationIATA', ), axis = 1)

df_obstruct3 = df.head(n).copy()
rate = 0.7
rate_typos = 0.4
df_obstruct3['Sex'] = df_obstruct3.apply(introduce_error_sex, args = (0.1, ), axis = 1)
df_obstruct3['Firstname'] = df_obstruct3['Firstname'].apply(lambda x: introduce_typos(x, rate))
df_obstruct3['Surname'] = df_obstruct3['Surname'].apply(lambda x: introduce_typos(x, rate))
df_obstruct3['Address'] = df_obstruct3['Address'].apply(lambda x: introduce_typos(x, rate))
df_obstruct3['DOB'] = df_obstruct3['DOB'].apply(lambda x: introduce_dob_typos(x, rate))
df_obstruct3['OriginIATA'] = df_obstruct3.apply(lambda row: introduce_error_airport(row, 'OriginIATA', geocrosswalk, 'city', rate), axis=1)
df_obstruct3['DestinationIATA'] = df_obstruct3.apply(lambda row: introduce_error_airport(row, 'DestinationIATA', geocrosswalk, 'city', rate), axis=1)
df_obstruct3['Nationality'] = df_obstruct3.apply(introduce_error_nat_city, args = (geocrosswalk, 'Nationality', 'HH_ISO', rate), axis = 1)
df_obstruct3['CityName'] = df_obstruct3.apply(introduce_error_nat_city, args = (geocrosswalk, 'CityName', 'City', rate), axis = 1)
df_obstruct3[['OriginLat', 'OriginLon', 'OriginCity', 'OriginCountry']] = df_obstruct3.apply(update_loc_airport, args = ('OriginIATA', ), axis = 1)
df_obstruct3[['DestinationLat', 'DestinationLon', 'DestinationCity', 'DestinationCountry']] = df_obstruct3.apply(update_loc_airport, args = ('DestinationIATA', ), axis = 1)

df_true = df.head(n).copy()
df_true['Mark'] = 'True'
df_obstruct1['Mark'] = 'Obs1'
df_obstruct2['Mark'] = 'Obs2'
df_obstruct3['Mark'] = 'Obs3'

df_appended = pd.concat([df_true, df_obstruct1], axis=0).reset_index(drop=True)
df_appended = pd.concat([df_appended, df_obstruct2], axis=0).reset_index(drop=True)
df_appended = pd.concat([df_appended, df_obstruct3], axis=0).reset_index(drop=True)
df_appended.shape

df_appended1 = df_appended.copy()
df_appended1['key'] = 1


ddf_ap1 = dd.from_pandas(df_appended1, npartitions=50)
ddf_ap2 = dd.from_pandas(df_appended1, npartitions=50)

cartesian_ddf = dd.merge(ddf_ap1, ddf_ap2, on='key').drop('key', axis=1)
cartesian_df = cartesian_ddf.compute()



cartesian_similarity_df = pd.DataFrame()
num_records = df_appended.shape[0]
max_distance = 20000


# Original
# gender_counts = df_appended['Sex'].str.lower().value_counts(normalize=True)
# origin_airport_counts = df_appended['OriginIATA'].str.lower().value_counts(normalize=True)
# origin_city_counts = df_appended['OriginCity'].str.lower().value_counts(normalize=True)
# origin_country_counts = df_appended['OriginCountry'].str.lower().value_counts(normalize=True)
# destination_airport_counts = df_appended['DestinationIATA'].str.lower().value_counts(normalize=True)
# destination_city_counts = df_appended['DestinationCity'].str.lower().value_counts(normalize=True)
# destination_country_counts = df_appended['DestinationCountry'].str.lower().value_counts(normalize=True)
# city_address_counts = df_appended['CityName'].str.lower().value_counts(normalize=True)
# country_address_counts = df_appended['Country of Address'].str.lower().value_counts(normalize=True)
# nationality_counts = df_appended['Nationality'].str.lower().value_counts(normalize=True)
# DOB_counts = df_appended['DOB'].value_counts(normalize=True)
# firstname_counts = df_appended['Firstname'].str.lower().value_counts(normalize=True)
# surname_counts = df_appended['Surname'].str.lower().value_counts(normalize=True)

# First Change
gender_counts = df_true['Sex'].str.lower().value_counts(normalize=True)
origin_airport_counts = df_true['OriginIATA'].str.lower().value_counts(normalize=True)
origin_city_counts = df_true['OriginCity'].str.lower().value_counts(normalize=True)
origin_country_counts = df_true['OriginCountry'].str.lower().value_counts(normalize=True)
destination_airport_counts = df_true['DestinationIATA'].str.lower().value_counts(normalize=True)
destination_city_counts = df_true['DestinationCity'].str.lower().value_counts(normalize=True)
destination_country_counts = df_true['DestinationCountry'].str.lower().value_counts(normalize=True)
city_address_counts = df_true['CityName'].str.lower().value_counts(normalize=True)
country_address_counts = df_true['Country of Address'].str.lower().value_counts(normalize=True)
nationality_counts = df_true['Nationality'].str.lower().value_counts(normalize=True)
DOB_counts = df_true['DOB'].value_counts(normalize=True)
firstname_counts = df_true['Firstname'].str.lower().value_counts(normalize=True)
surname_counts = df_true['Surname'].str.lower().value_counts(normalize=True)


# String similarity for first names
cartesian_similarity_df[['FNSimilarity', 'FN1', 'FN2', 'FN_rarity1', 'FN_rarity2', 'FN_prob1', 'FN_prob2']] = cartesian_df.apply(lambda row: string_similarity(row['Firstname_x'].lower(), row['Firstname_y'].lower(), firstname_counts, num_records), axis=1)

# String similarity for surnames
cartesian_similarity_df[['SNSimilarity', 'SN1', 'SN2', 'SN_rarity1', 'SN_rarity2', 'SN_prob1', 'SN_prob2']] = cartesian_df.apply(lambda row: string_similarity(row['Surname_x'].lower(), row['Surname_y'].lower(), surname_counts, num_records), axis=1)

# String similarity for DOB
cartesian_similarity_df[['DOBSimilarity', 'DOB1', 'DOB2', 'DOB_rarity1', 'DOB_rarity2', 'DOB_prob1', 'DOB_prob2']] = cartesian_df.apply(lambda row: string_similarity(row['DOB_x'].lower(), row['DOB_y'].lower(), DOB_counts, num_records), axis=1)

# Age similarity
cartesian_similarity_df['AgeSimilarity'] = cartesian_df.apply(lambda row: age_similarity_score(row['DOB_x'], row['DOB_y']), axis=1)

# Address similarity 
cartesian_similarity_df[['strAddressSimilarity', 'jcdAddressSimilarity']] = cartesian_df.apply(lambda row: address_str_similarity_score(row['Address_x'], row['Address_y']), axis=1)

# City address match
cartesian_similarity_df['cityAddressMatch'] = cartesian_df.apply(lambda row: location_matching(row['CityName_x'], row['CityName_y']), axis=1)

# City address rarity and probability
cartesian_similarity_df[['cityAddressRarity1', 'cityAddressProb1']] = cartesian_df['CityName_x'].str.lower().apply(lambda x: count_likelihood2(x, city_address_counts, num_records))
cartesian_similarity_df[['cityAddressRarity2', 'cityAddressProb2']] = cartesian_df['CityName_y'].str.lower().apply(lambda x: count_likelihood2(x, city_address_counts, num_records))

# Country address match
cartesian_similarity_df['countryAddressMatch'] = cartesian_df.apply(lambda row: location_matching(row['Country of Address_x'], row['Country of Address_y']), axis=1)

# Country address rarity and probability
cartesian_similarity_df[['countryAddressRarity1', 'countryAddressProb1']] = cartesian_df['Country of Address_x'].str.lower().apply(lambda x: count_likelihood2(x, country_address_counts, num_records))
cartesian_similarity_df[['countryAddressRarity2', 'countryAddressProb2']] = cartesian_df['Country of Address_y'].str.lower().apply(lambda x: count_likelihood2(x, country_address_counts, num_records))

# Sex match and corresponding metrics
cartesian_similarity_df['sexMatch'] = cartesian_df.apply(lambda row: location_matching(row['Sex_x'].lower(), row['Sex_y'].lower()), axis=1)
cartesian_similarity_df[['sexRarity1', 'sexProb1']] = cartesian_df['Sex_x'].str.lower().apply(lambda x: count_likelihood2(x, gender_counts, num_records))
cartesian_similarity_df[['sexRarity2', 'sexProb2']] = cartesian_df['Sex_y'].str.lower().apply(lambda x: count_likelihood2(x, gender_counts, num_records))

# Nationality match and corresponding metrics
cartesian_similarity_df['natMatch'] = cartesian_df.apply(lambda row: location_matching(row['Nationality_x'].lower(), row['Nationality_y'].lower()), axis=1)
cartesian_similarity_df[['natRarity1', 'natProb1']] = cartesian_df['Nationality_x'].str.lower().apply(lambda x: count_likelihood2(x, nationality_counts, num_records))
cartesian_similarity_df[['natRarity2', 'natProb2']] = cartesian_df['Nationality_y'].str.lower().apply(lambda x: count_likelihood2(x, nationality_counts, num_records))

# Origin airport match and corresponding metrics
cartesian_similarity_df['originAirportMatch'] = cartesian_df.apply(lambda row: location_matching(row['OriginIATA_x'].lower(), row['OriginIATA_y'].lower()), axis=1)
cartesian_similarity_df[['originAirportRarity1', 'originAirportProb1']] = cartesian_df['OriginIATA_x'].str.lower().apply(lambda x: count_likelihood2(x, origin_airport_counts, num_records))
cartesian_similarity_df[['originAirportRarity2', 'originAirportProb2']] = cartesian_df['OriginIATA_y'].str.lower().apply(lambda x: count_likelihood2(x, origin_airport_counts, num_records))

# Destination airport match and corresponding metrics
cartesian_similarity_df['destinationAirportMatch'] = cartesian_df.apply(lambda row: location_matching(row['DestinationIATA_x'].lower(), row['DestinationIATA_y'].lower()), axis=1)
cartesian_similarity_df[['destinationAirportRarity1', 'destinationAirportProb1']] = cartesian_df['DestinationIATA_x'].str.lower().apply(lambda x: count_likelihood2(x, destination_airport_counts, num_records))
cartesian_similarity_df[['destinationAirportRarity2', 'destinationAirportProb2']] = cartesian_df['DestinationIATA_y'].str.lower().apply(lambda x: count_likelihood2(x, destination_airport_counts, num_records))

# Origin city match and corresponding metrics
cartesian_similarity_df['originCityMatch'] = cartesian_df.apply(lambda row: location_matching(row['OriginCity_x'].lower(), row['OriginCity_y'].lower()), axis=1)
cartesian_similarity_df[['originCityRarity1', 'originCityProb1']] = cartesian_df['OriginCity_x'].str.lower().apply(lambda x: count_likelihood2(x, origin_city_counts, num_records))
cartesian_similarity_df[['originCityRarity2', 'originCityProb2']] = cartesian_df['OriginCity_y'].str.lower().apply(lambda x: count_likelihood2(x, origin_city_counts, num_records))

# Destination city match and corresponding metrics
cartesian_similarity_df['destinationCityMatch'] = cartesian_df.apply(lambda row: location_matching(row['DestinationCity_x'].lower(), row['DestinationCity_y'].lower()), axis=1)
cartesian_similarity_df[['destinationCityRarity1', 'destinationCityProb1']] = cartesian_df['DestinationCity_x'].str.lower().apply(lambda x: count_likelihood2(x, destination_city_counts, num_records))
cartesian_similarity_df[['destinationCityRarity2', 'destinationCityProb2']] = cartesian_df['DestinationCity_y'].str.lower().apply(lambda x: count_likelihood2(x, destination_city_counts, num_records))

# Origin country match and corresponding metrics
cartesian_similarity_df['originCountryMatch'] = cartesian_df.apply(lambda row: location_matching(row['OriginCountry_x'].lower(), row['OriginCountry_y'].lower()), axis=1)
cartesian_similarity_df[['originCountryRarity1', 'originCountryProb1']] = cartesian_df['OriginCountry_x'].str.lower().apply(lambda x: count_likelihood2(x, origin_country_counts, num_records))
cartesian_similarity_df[['originCountryRarity2', 'originCountryProb2']] = cartesian_df['OriginCountry_y'].str.lower().apply(lambda x: count_likelihood2(x, origin_country_counts, num_records))

# Destination country match and corresponding metrics
cartesian_similarity_df['destinationCountryMatch'] = cartesian_df.apply(lambda row: location_matching(row['DestinationCountry_x'].lower(), row['DestinationCountry_y'].lower()), axis=1)
cartesian_similarity_df[['destinationCountryRarity1', 'destinationCountryProb1']] = cartesian_df['DestinationCountry_x'].str.lower().apply(lambda x: count_likelihood2(x, destination_country_counts, num_records))
cartesian_similarity_df[['destinationCountryRarity2', 'destinationCountryProb2']] = cartesian_df['DestinationCountry_y'].str.lower().apply(lambda x: count_likelihood2(x, destination_country_counts, num_records))
# For the geographical similarity, ensure you have 'lon_o', 'lat_o', 'lon_d', and 'lat_d' defined
# Example for origin similarity (adjust similarly for destination and others)
cartesian_similarity_df[['originSimilarity', 'originExpScore']] = cartesian_df.apply(lambda row: location_similarity_score(row['OriginLon_x'], row['OriginLat_x'], row['OriginLon_y'], row['OriginLat_y'], max_distance), axis=1, result_type='expand')
cartesian_similarity_df[['destinationSimilarity', 'destinationExpScore']] = cartesian_df.apply(lambda row: location_similarity_score(row['DestinationLon_x'], row['DestinationLat_x'], row['DestinationLon_y'], row['DestinationLat_y'], max_distance), axis=1, result_type='expand')
cartesian_similarity_df['Class'] = cartesian_df.apply(lambda row: 1 if row['Travel Doc Number_x'] == row['Travel Doc Number_y'] else 0, axis=1)
cartesian_similarity_df['Mark'] = cartesian_df['Mark_x'] + "-" + cartesian_df['Mark_y']
cartesian_similarity_df['StandardizedMark'] = cartesian_similarity_df['Mark'].apply(standardize_mark)
print(cartesian_similarity_df['StandardizedMark'].unique())
# cartesian_similarity_df.to_csv('test/cartesian_similarity_df.csv')



# cartesian_df.to_csv('test/cartesian_df.csv')
# cartesian_similarity_df.to_csv('test/cartesian_similarity_df.csv')
results = []
metrics_df = pd.DataFrame(columns=['TestMark', 'MCC', 'ROC-AUC', 'Precision', 'Recall', 'PR-AUC'])
test_marks = ['Obs2-Obs2', 'Obs2-Obs3', 'Obs1-Obs2', 'Obs2-True', 'Obs3-Obs3', 'Obs1-Obs3','Obs3-True', 'Obs1-Obs1', 'Obs1-True', 'True-True', 'All-Data']
for mark in test_marks:
    if mark == 'All-Data':
        results.append(run_xgboost_classification_v2(cartesian_similarity_df, include_all_for_train_test=True, result_path='test_result_all_data'))
    else:
        result_folder = f'test_result_{mark}'
        results.append(run_xgboost_classification_v2(cartesian_similarity_df, test_mark=mark, result_path=result_folder))

# Convert list to DataFrame
metrics_df = pd.DataFrame(results, columns=['Test Mark', 'MCC', 'ROC-AUC', 'Precision', 'Recall', 'PR-AUC'])

    # metrics_df = metrics_df.append(metrics_dict, ignore_index=True)

# Save the DataFrame to a CSV file after completing all iterations
metrics_df.to_csv('test_result/model_evaluation_metrics.csv', index=False)





