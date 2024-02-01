from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import re
import requests
import pandas as pd
import os
from requests.auth import HTTPBasicAuth
from utils import *

#### Options ####
# Run browser with no window
CONF_HEADLESS_BROWSER = True

# Reading Source files
url_sources = pd.read_csv('sources_list.csv')
df = pd.read_csv('input.csv')
df = pd.merge(df, url_sources, on='nombre_corto', how='left')

#### Processing Functions ####
# For each portal, we need to write a function that finds the files to download
def download_sns():
    # Open in browser
    driver = webdriver.Firefox(options=options)
    driver.get(base_url)
    # Click the year
    click_element_by_text(driver, next_needed_year)

    # Click the month
    click_element_by_text(driver, next_needed_month_text)

    # Find the link to the Excel file
    content = driver.page_source
    excel_links = find_links_to_excel_files(content)

    # Download the Excel file
    download_excel_files_from_url(excel_links, folder_name)
    driver.close()
    return excel_links

def download_ejercito():
    response = requests.get(base_url)

    # Construct the URL
    # Example:https://www.ejercito.mil.do/transparencia/images/docs/recursos_humanos/nomina/2023/NOMINA%20G-1%20ERD%20OCTUBRE%202023.xls
    ejercito_url = 'https://www.ejercito.mil.do/transparencia/images/docs/recursos_humanos/nomina/'+next_needed_year+'/NOMINA%20G-1%20ERD%20'+next_needed_month_text.upper()+'%20'+next_needed_year+'.xls'

    # The site always returns a 200 response, even if the file doesn't exist
    # So we need to check the response contains "Página no encontrada"
    response = requests.get(ejercito_url)
    if "Página no encontrada" in response.text:
        raise("No Excel file found:", ejercito_url)
    else:
        print("Found Excel file:", ejercito_url)

    # Download the Excel file
    download_excel_files_from_url([ejercito_url], folder_name)
    return [ejercito_url]

def download_inaipi():
    response = requests.get(base_url)
    available_links = find_links_matching_all(response, [f'nominas-{next_needed_year}'])
    
    response = requests.get(available_links[0])
    available_links2 = find_links_matching_all(response, [f'nominas-{next_needed_month_text.lower()}-{next_needed_year}'])
    
    response = requests.get(available_links2[0])
    available_links3 = find_links_matching_all(response, [f'nominas-{next_needed_month_text.lower()}-{next_needed_year}', 'download'])

    download_excel_files_from_url(available_links3, folder_name, filename_from_headers=True)

    return available_links3
    
def download_dga():
    # Open in headless browser
    driver = webdriver.Firefox(options=options)
    driver.get(base_url)
    
    # Click the Nomina
    click_element_by_text(driver, 'Nómina')

    # Click the year
    click_element_by_text(driver, next_needed_year, partial_match=True)

    # find the link to the desired document
    available_links = find_links_matching_all(driver,  [f'{next_needed_month_text.lower()}',
                                                                    f'{next_needed_year}',
                                                                    'xlsx'])
    
    download_excel_files_from_url(available_links, folder_name)
    return available_links
    
def download_inapa():
    # Open in headless browser
    driver = webdriver.Firefox(options=options)
    driver.get(base_url)

    # Click the year
    click_element_by_text(driver, next_needed_year)

    # Click the month
    click_element_by_text(driver, next_needed_month_text.upper())

    available_links = find_links_matching_all(driver,  [f'{next_needed_month_text.lower()}',
                                                        f'{next_needed_year}',
                                                        'download'])
    
    # Click Nominas Adicionales
    click_element_by_text(driver, 'NOMINAS ADICIONALES')

    available_links = find_links_matching_all(driver,  [f'{next_needed_month_text.lower()}',
                                                        f'{next_needed_year}',
                                                        'download'])

    download_excel_files_from_url(available_links, folder_name, filename_from_headers=True)
    driver.close()
    return available_links

def download_caasd():
    # In progress
    return []

def download_ln():
    # Development paused because the site is down
    response = requests.get(f'https://loterianacional.gob.do/transparencia/recursos-humanos/nomina-de-empleados/periodo?p={next_needed_year}')
    available_links = find_links_matching_all(response, [f'{next_needed_month_text.upper()}',
                                                         f'{next_needed_year}'])

def download_feda():
    # Open in headless browser
    driver = webdriver.Firefox(options=options)
    driver.get(base_url)

    # Click the year
    click_element_by_text(driver, next_needed_year, partial_match=True)

    # Click the month
    click_element_by_text(driver, next_needed_month_text, partial_match=True)

    available_links = find_links_matching_all(driver,  [f'{next_needed_month_text.lower()}',
                                                        f'{next_needed_year}',
                                                        'download'])
    
    download_excel_files_from_url(available_links, folder_name, filename_from_headers=True)
    driver.close()
    return available_links

def download_intrant():
    # Open in headless browser
    driver = webdriver.Firefox(options=options)

    # this site actually has 3 links
    carpetas = ['nomina-militares','empleados-contratados','empleados-fijos']
    for carpeta in carpetas:
        driver.get(f'{base_url}/{carpeta}')
        # Click the year
        click_element_by_text(driver, next_needed_year, partial_match=True)
        available_links = find_links_matching_all(driver,  [f'{next_needed_month_text.lower()}', f'{next_needed_year}'])
        download_excel_files_from_url(available_links, folder_name)
    driver.close()
    return available_links


# main function
if __name__ == "__main__":
    for i in range(len(df)):
        print(df['nombre_corto'][i])
        # common variables
        base_url = df['portal'][i].strip()
        domain = re.findall(r'^(https?://[^/]+)', base_url)[0]
        next_needed_date = df['query_date'][i]
        next_needed_year, next_needed_month = next_needed_date.split('_')
        next_needed_month_text = month_names_dict[next_needed_month]
        folder_name = f"downloads/{next_needed_date}/{df['nombre_corto'][i]}"
        options = webdriver.FirefoxOptions()
        if CONF_HEADLESS_BROWSER:
            options.add_argument('--headless')
        # calling the download function
        eval(f"download_{df['nombre_corto'][i].lower()}")()