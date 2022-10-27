"""
Investigation of the importance of device performance on the number of citations
Prepare data for analysis
"""
from datetime import datetime
import os
import pickle

import pandas as pd

from get_data_from_crossref import download_citation_data

UPPDATE_CITATION_DATA_FROM_CROSSREF = False

#%% File paths
fileName_data = 'Perovskite_database_content_all_data.csv'
path_data_folder = os.path.join(os.path.abspath(os.getcwd()), "data")
path_data = os.path.join(path_data_folder, fileName_data)
doi_path = os.path.join(path_data_folder, "DOIdata")


#%% Helper functions
def data_columns_to_use():
    """ Returns a list of the data columns the app will use"""
    return [
        'Ref_DOI_number',
        'Ref_publication_date',
        'Ref_journal',
        'JV_default_Voc',
        'JV_default_Jsc',
        'JV_default_FF',
        'JV_default_PCE',
        'JV_light_intensity',
        'Perovskite_band_gap',
        'Perovskite_composition_short_form',
        'Cell_architecture',
    ]


def get_data(path_data):
    # Load data downloaded from the perovskite database
    data = pd.read_csv(path_data, low_memory=False)
    # Pick out the columns to use
    data = data[data_columns_to_use()]
    # Drop measurements at high and low light intensities
    data = data[(data['JV_light_intensity'] > 90) & (data['JV_light_intensity'] < 110)]
    # Drop rows with nan values in the PCE column
    data.dropna(subset=["JV_default_PCE"], inplace = True)
    # Filer out the device with the highest PCE for each paper
    data_best = data.sort_values('JV_default_PCE').drop_duplicates(["Ref_DOI_number"], keep='last')

    return data_best


#%% Get the data for the best device for each article in the database
data = get_data(path_data)
# Extract the DOI numbers for all those papers
doi_numbers = data['Ref_DOI_number'].tolist()

#%% Get citation data
if UPPDATE_CITATION_DATA_FROM_CROSSREF:
    download_citation_data(doi_numbers, doi_path)

# Read in citation data extracted from crossref for selected papers
with open(doi_path, 'rb') as f:
    citationData = pickle.load(f)

#%%
reference_counts = []
journal = []
date = []
for i in range(len(citationData)):
    reference_counts.append(citationData['Dict'][i]['is-referenced-by-count'])
    journal.append(citationData['Dict'][i]['container-title'][0])
    date_temp = citationData['Dict'][i]['created']['date-parts'][0]
    # Convert datetime string to datetime format
    date_temp = datetime.strptime(str(date_temp)[1:-1], '%Y, %m, %d').date()    
    date.append(date_temp)
    
#%% Extract relevant data
data_dict = {'DOI': citationData['DOI'].tolist(), 'Citations': reference_counts, 'Journal': journal,
             'Publication_date': date,}
data_citation = pd.DataFrame(data_dict)

#%% Merge the interesting data
data_m = pd.merge(data, data_citation, left_on='Ref_DOI_number', right_on='DOI')

#%% Save data as a csv file
data_m.to_csv(os.path.join(path_data_folder, 'Citation_data.csv'))

