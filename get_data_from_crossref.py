"""
Download citation data from crossref based on doi numbers
Use crossref (https://www.crossref.org/) to extract metadata
"""

import datetime
import os
import pickle

from crossref.restful import Works, Etiquette
import pandas as pd

MY_ETIQUETTE = Etiquette('Perovskite solar', 'version 1', '', 'jacobsson.jesper.work@gmail.com')

def get_doi_for_papers_on_file(doi_path):
    """Read in DOI numbers of papers which data already have been downloaded"""
    if os.path.exists(doi_path):
        with open(doi_path, 'rb') as f:
            citation_data_on_file = pickle.load(f)
            list_of_saved_doi = citation_data_on_file['DOI'].tolist()
    else:
        citation_data_on_file = []
        list_of_saved_doi = []

    return citation_data_on_file, list_of_saved_doi


def download_citation_data(doi_numbers, doi_path, update_all_data=False):
    """Extract citation data from CrossRf based on the DOI number
    Stor all downloaded reference data in a pickle file located at DOIPath"""

    # List of DOI numbers to download data for
    citation_data_on_file, list_of_saved_doi = get_doi_for_papers_on_file(doi_path=doi_path)
    if update_all_data:
        doi_to_download = list(set(doi_numbers))
    else:
        doi_to_download = list(set(doi_numbers) - set(list_of_saved_doi))

    # Setting up a session connecting to the crossref API
    works = Works(etiquette=MY_ETIQUETTE)

    # Download reference data for all DOI not previously downloaded
    papers = []
    for i, DOI in enumerate(doi_to_download):
        print(f'Searching for citation data for paper on row {i}')  # for keeping track of progress during development
        # Get the metadata for the paper from Crossref
        try:
            paper = works.doi(DOI)          
            if type(paper) == dict:
                papers.append({'DOI': DOI, 'Dict': paper})
            else:
                print(f'Failed to download data for: {DOI}')                 
        except:
            print(f'Failed to download data for: {DOI}')  
 
    # Convert downloaded data to a data frame
    new_citation_data = pd.DataFrame(papers)

    # Update citation data
    if update_all_data:
        uppdated_citation_data = new_citation_data
    else:
        uppdated_citation_data = pd.concat([citation_data_on_file, new_citation_data], ignore_index=True)

    # Save the downloaded reference information
    try:
        with open(doi_path, 'wb') as f:
            pickle.dump(uppdated_citation_data, f)
    except:
        print('Failed to save new DOI data to reference file')


