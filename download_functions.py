from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import re
import requests
import pandas as pd
import os
from requests.auth import HTTPBasicAuth
from utils import *

df = pd.read_excel('Lista Web Fuentes Nómina Pública.xlsx')


#### Processing Functions ####
# For each portal, we need to write a function that finds the files to download

def download_sns(df, i):
    base_url = df['Portal'][i].strip()
    next_needed_date = df['next_date'][i]
    next_needed_year, next_needed_month = next_needed_date.split('_')
    next_needed_month_text = month_names_dict[next_needed_month]
    folder_name = f"downloads/{next_needed_date}/{df['nombre_corto'][i]}"

    # Open in headless browser
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    try:
        driver.get(base_url)
        # Click the year
        search_criteria = f"//*[text()='{next_needed_year}']"
        date_elements = driver.find_elements(By.XPATH, search_criteria)
        date_elements[0].click()
        time.sleep(3)

        # Click the month
        search_criteria = f"//*[text()='{next_needed_month_text}']"
        date_elements = driver.find_elements(By.XPATH, search_criteria)
        date_elements[0].click()
        time.sleep(3)

        # Find the link to the Excel file
        content = driver.page_source
        excel_links = find_links_to_excel_files(content)

        # Download the Excel file
        download_excel_files_from_url(excel_links, folder_name)
        driver.close()
    except:
        print("Error with URL:", df['Portal'][i])
        driver.close()
        pass
    return excel_links

def download_ejercito(df,i):
    base_url = df['Portal'][i].strip()
    next_needed_date = df['next_date'][i]
    next_needed_year, next_needed_month = next_needed_date.split('_')
    next_needed_month_text = month_names_dict[next_needed_month]
    folder_name = f"downloads/{next_needed_date}/{df['nombre_corto'][i]}"
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

def download_inaipi(df, i):
    base_url = df['Portal'][i].strip()
    domain = re.findall(r'^(https?://[^/]+)', base_url)[0]
    next_needed_date = df['next_date'][i]
    next_needed_year, next_needed_month = next_needed_date.split('_')
    next_needed_month_text = month_names_dict[next_needed_month]
    folder_name = f"downloads/{next_needed_date}/{df['nombre_corto'][i]}"
    response = requests.get(base_url)

    soup = BeautifulSoup(response.content, 'html.parser')
    a_tags = soup.find_all('a')
    # filter links with the format "nominas-2023"
    available_links = [domain + '/' + a['href'] for a in a_tags if 'href' in a.attrs and f'nominas-{next_needed_year}' in a['href']]
    if len(available_links) == 0:
        raise("Expected link not found:", f'nominas-{next_needed_year}')
    
    response = requests.get(available_links[0])
    soup2 = BeautifulSoup(response.content, 'html.parser')
    a_tags2 = soup2.find_all('a')
    # filter links with the format "nominas-diciembre-2023"
    available_links2 = [domain + '/' + a['href'] for a in a_tags2 if 'href' in a.attrs and f'nominas-{next_needed_month_text.lower()}-{next_needed_year}' in a['href']]

    response = requests.get(available_links2[0])
    soup3 = BeautifulSoup(response.content, 'html.parser')
    a_tags3 = soup3.find_all('a')

    available_links3 = [domain + '/' + a['href'] for a in a_tags3 if 'href' in a.attrs and f'nominas-{next_needed_month_text.lower()}-{next_needed_year}' in a['href'] and 'download' in a['href']]

    download_excel_files_from_url(available_links3, folder_name, filename_from_headers=True)

    return available_links3
    
def download_dga(df, i):
    base_url = df['Portal'][i].strip()
    domain = re.findall(r'^(https?://[^/]+)', base_url)[0]
    next_needed_date = df['next_date'][i]
    next_needed_year, next_needed_month = next_needed_date.split('_')
    next_needed_month_text = month_names_dict[next_needed_month]
    folder_name = f"downloads/{next_needed_date}/{df['nombre_corto'][i]}"
    response = requests.get(base_url)

    # Open in headless browser
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    driver.get(base_url)
    
    # Click the Nomina
    search_criteria = f"//*[text()='Nómina']"
    date_elements = driver.find_elements(By.XPATH, search_criteria)
    date_elements[0].click()
    time.sleep(3)

    # Click the year
    search_criteria = f"//*[text()={next_needed_year}]"
    date_elements = driver.find_elements(By.XPATH, search_criteria)
    # filter empty elements
    date_elements = [el for el in date_elements if el.text]
    date_elements[0].click()
    time.sleep(3)

    # find the link to the desired document
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    a_tags = soup.find_all('a')
    available_links = [domain + '/' + a['href'] for a in a_tags if
                        'href' in a.attrs and
                         f'{next_needed_month_text.lower()}' in a['href'] and
                         f'{next_needed_year}' in a['href'] and
                         'xlsx' in a['href']
                        ]
    download_excel_files_from_url(available_links, folder_name)
    return available_links
    

def download_inapa(df, i):
    base_url = df['Portal'][i].strip()
    domain = re.findall(r'^(https?://[^/]+)', base_url)[0]
    next_needed_date = df['next_date'][i]
    next_needed_year, next_needed_month = next_needed_date.split('_')
    next_needed_month_text = month_names_dict[next_needed_month]
    folder_name = f"downloads/{next_needed_date}/{df['nombre_corto'][i]}"
    # Open in headless browser
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    driver.get(base_url)

    # Click the year
    search_criteria = f"//*[text()='{next_needed_year}']"
    date_elements = driver.find_elements(By.XPATH, search_criteria)
    date_elements[0].click()
    time.sleep(3)

    # Click the month
    search_criteria = f"//*[text()='{next_needed_month_text.upper()}']"
    date_elements = driver.find_elements(By.XPATH, search_criteria)
    date_elements[0].click()
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    a_tags = soup.find_all('a')
    available_links = [domain + '/' + a['href'] for a in a_tags if
                        'href' in a.attrs and
                         f'{next_needed_month_text.lower()}' in a['href'] and
                         f'{next_needed_year}' in a['href'] and
                         'download' in a['href']
                        ]
    
    # Click Nominas Adicionales
    search_criteria = f"//*[text()='NOMINAS ADICIONALES']"
    date_elements = driver.find_elements(By.XPATH, search_criteria)
    date_elements[0].click()
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    a_tags = soup.find_all('a')

    available_links+=[domain + '/' + a['href'] for a in a_tags if
                        'href' in a.attrs and
                         f'{next_needed_month_text.lower()}' in a['href'] and
                         f'{next_needed_year}' in a['href'] and
                         'download' in a['href']
                        ]
    
    download_excel_files_from_url(available_links, folder_name, filename_from_headers=True)
    driver.close()
    return available_links

def download_caasd(df, i):
    base_url = df['Portal'][i].strip()
    domain = re.findall(r'^(https?://[^/]+)', base_url)[0]
    next_needed_date = df['next_date'][i]
    next_needed_year, next_needed_month = next_needed_date.split('_')
    next_needed_month_text = month_names_dict[next_needed_month]
    folder_name = f"downloads/{next_needed_date}/{df['nombre_corto'][i]}"

    # In progress
    return []


download_caasd(df, 5)