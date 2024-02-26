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
    download_excel_files_from_url(available_links, folder_name, filename_from_headers=True)
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

# def download_indrhi():
#     # Open in headless browser
#     driver = webdriver.Firefox(options=options)
#     driver.get(base_url)
    
#     # Click the Nomina
#     click_element_by_text(driver, 'Nóminas Contratados', sleep_time=8)

#     # Click the year
#     click_element_by_text(driver, "Año "+next_needed_year, sleep_time=8)
#     print("Año "+next_needed_year)

#     # find the link to the desired document
#     available_links = find_links_matching_all(driver,  [f'{next_needed_month_text.lower()}',
#                                                                     f'{next_needed_year}',
#                                                                     'xlsx'])
#        # Find the link to the Excel file
#     content = driver.page_source
#     # print(content)
#     excel_links = find_links_to_excel_files(content)

#     print(available_links)
#     print(excel_links)
    
#     download_excel_files_from_url(available_links, folder_name)
#     return available_links

def download_dgii():
     # In progress
    return []

def download_ayuntamientosantiago():
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


def download_opret():
    # Open in browser
    driver = webdriver.Firefox(options=options)
    driver.get(base_url)
    # Click the year
    click_element_by_text(driver, next_needed_year)
    urls = ["https://www.opret.gob.do/Documentos/Recursos Humanos/NÓMINA EMPLEADOS FIJO METRO " + next_needed_month_text.upper()+" "+next_needed_year+".xls",
            "https://www.opret.gob.do/Documentos/Recursos Humanos/NÓMINA EMPLEADOS FIJO LINEA 2C " + next_needed_month_text.upper()+" "+next_needed_year+".xls", 
            "https://www.opret.gob.do/Documentos/Recursos Humanos/NÓMINA EMPLEADOS TEMPORERO OPRET " + next_needed_month_text.upper()+" "+next_needed_year+".xls"]

    # The site always returns a 200 response, even if the file doesn't exist
    # So we need to check the response contains "Página no encontrada"
    for url in urls :
        response = requests.get(url)
        if "Página no encontrada" in response.text:
            raise("No Excel file found:", url)
        else:
            print("Found Excel file:", url)

        # Download the Excel file
        download_excel_files_from_url([url], folder_name)

    driver.close()
    return urls

def download_senado():
    # Open in browser
    driver = webdriver.Firefox(options=options)
    driver.get(base_url)
    # Click the year
    click_element_by_text(driver, next_needed_year, sleep_time=30)

    # Click the month
    click_element_by_text(driver, next_needed_month_text, sleep_time=30)

    #Click the nomina
    click_element_by_text(driver, "Nómina Sueldos Fijos "+next_needed_month_text+"-"+next_needed_year, sleep_time=15)

    available_links = find_links_matching_all(driver,  [f'{next_needed_month_text.lower()}',
                                                        f'{next_needed_year}',
                                                        'nomina-sueldos-fijos'], without_domain=True)

    # Download the Excel file
    download_excel_files_from_url(available_links, folder_name, filename_from_headers=True)
    driver.close()
    return available_links
        
# def download_inespre():
#     # Open in browser
#     driver = webdriver.Firefox(options=options)
#     driver.get(base_url)
#     # Click the year
#     click_element_by_text(driver, next_needed_year, partial_match=True)

#     # # find the link to the desired document
#     available_links = find_links_matching_all(driver,  [f'{next_needed_month_text.lower()}',
#                                                                     f'{next_needed_year}',
#                                                                     'xlsx'])
    
#     print(available_links)
 
#     # Find the link to the Excel file
#     content = driver.page_source
#     # print(available_links)
#     excel_links = find_links_to_excel_files(content)
#     print(excel_links)
#     # Download the Excel file
#     download_excel_files_from_url(available_links, folder_name, allow_redirects=True)
#     driver.close()
#     return available_links
        

def download_dncd():
    # Open in headless browser
    driver = webdriver.Firefox(options=options)
    driver.get(base_url)

    # Click the year
    click_element_by_text(driver, next_needed_year)

    available_links = find_links_matching_all(driver,  [f'{next_needed_month_text.lower()}',
                                                        f'{next_needed_year}',
                                                        'download'])
    # Download the Excel file
    download_excel_files_from_url(available_links, folder_name, filename_from_headers=True, allow_redirects=False, split_arg="Nomina/")
    driver.close()
    return available_links

def download_inposdom():
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

def download_bagricola():
    # Open in headless browser
    driver = webdriver.Firefox(options=options)
    driver.get(base_url)

    # Click the year
    click_element_by_text(driver, next_needed_year, partial_match=True)

    # find the link to the desired document
    available_links = find_links_matching_all(driver,  [f'{next_needed_month_text.upper()}',
                                                                    f'{next_needed_year}',
                                                                    'xlsx'], without_domain=True)
    
    download_excel_files_from_url(available_links, folder_name)
    driver.close()
    return available_links

def download_sie():
    # Open in headless browser
    driver = webdriver.Firefox(options=options)
    driver.get(base_url)

    #Find the links 
    available_links = find_links_matching_all(driver,  [f'{next_needed_month_text.upper()}',
                                                        f'{next_needed_year}'], without_domain=True)
    
    download_excel_files_from_url(available_links, folder_name)
    driver.close()
    return available_links

def download_uasd():
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

def download_minc():
    list = [
        'Nómina Personal Fijo',
        'Nómina Personal Vigilancia',
        'Nómina Personal Temporal'
    ]

    driver = webdriver.Firefox(options=options)

    for element in list:
        # Open in browser
        driver.get(base_url)

        # Click the Nomina
        click_element_by_text(driver, element)

        # Click the year
        click_element_by_text(driver, next_needed_year)

        if next_needed_year != "2023" and (element == "Nómina Personal Fijo" or element == "Nómina Personal Vigilancia"):
            # Click the month
            click_element_by_text(driver, next_needed_month_text)

        #Find the links 
        available_links = find_links_matching_all(driver,  [f'{next_needed_month_text.lower()}', 'download'])

        # Download the Excel file
        download_excel_files_from_url(available_links, folder_name, filename_from_headers=True)
    driver.close()

def download_miderec():
     # Open in browser
    driver = webdriver.Firefox(options=options)
    driver.get(base_url)
    # Click the year
    click_element_by_text(driver, next_needed_year)

    # Click the month
    click_element_by_text(driver, next_needed_month_text)

    #Find the links 
    available_links = find_links_matching_all(driver,  ['task=file.download'], without_domain=True)

    # Download the Excel file
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9'}
    download_excel_files_from_url(available_links, folder_name, filename_from_headers=True, headers=headers)
    driver.close()
    return available_links


def download_micm():
     # Open in browser
    driver = webdriver.Firefox(options=options)
    driver.get(base_url)
    # Click the year
    click_element_by_text(driver, "Nómina " +next_needed_year)

    # Click the month
    click_element_by_text(driver, next_needed_month_text + " ")

     # Find the link to the Excel file
    content = driver.page_source
    excel_links = find_links_to_excel_files(content, domain="https://www.micm.gob.do")

    # Download the Excel file
    download_excel_files_from_url(excel_links, folder_name)
    driver.close()
    return excel_links

def download_mmujer():
    list = [
       'Nómina empleado fijos', 'Nómina empleados contratados',
    ]

    driver = webdriver.Firefox(options=options)

    for element in list:
        # Open in browser
        driver.get(base_url)

        # Click the Nomina
        click_element_by_text(driver, element)

        # Click the year
        click_element_by_text(driver, next_needed_year)

        if next_needed_year == "2023" and element == 'Nómina empleados contratados':
            # Click the month
            click_element_by_text(driver, next_needed_month_text)

        #Find the links 
        available_links = find_links_matching_all(driver,  [f'{next_needed_month_text.lower()}', 'download'])

        # Download the Excel file
        download_excel_files_from_url(available_links, folder_name, filename_from_headers=True, allow_redirects=False, split_arg=next_needed_year+"/")
    driver.close()
    return available_links

def download_mopc():
     # Open in browser
    driver = webdriver.Firefox(options=options)
    driver.get(base_url)
    # Click the year
    click_element_by_text(driver, next_needed_year)

    #Find the links 
    available_links = find_links_matching_all(driver,  [f'{next_needed_month_text.lower()}', f'{next_needed_year}','.xlsx'])

    # Download the Excel file
    download_excel_files_from_url(available_links, folder_name)
    driver.close()
    return available_links

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

def download_mitur():
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

def download_omsa():
    list = [
        ' Nómina contratados', 'Nómina fija',
    ]

    driver = webdriver.Firefox(options=options)

    for element in list:
        # Open in browser
        driver.get(base_url)

        # Click the Nomina
        click_element_by_text(driver, element)

        # Click the year
        click_element_by_text(driver, next_needed_year)

        #Find the links 
        available_links = find_links_matching_all(driver,  [f'{next_needed_month_text.lower()}', f'{next_needed_year}', 'download'])

        # Download the Excel file
        download_excel_files_from_url(available_links, folder_name, filename_from_headers=True)

    driver.close()
    return available_links

def download_dgba():
    # Open in headless browser
    driver = webdriver.Firefox(options=options)
    driver.get(base_url)

    # Click the year
    click_element_by_text(driver, "Nómina " + next_needed_year, partial_match=True)

    # Click the month
    click_element_by_text(driver, next_needed_month_text, partial_match=True)

    available_links = find_links_matching_all(driver,  [f'{next_needed_month_text.lower()}',
                                                        f'{next_needed_year}',
                                                        'download'])
    
    download_excel_files_from_url(available_links, folder_name, filename_from_headers=True,  allow_redirects=False, split_arg=next_needed_month_text.lower()+"/")
    driver.close()
    return available_links

def download_mide():
    # Open in headless browser
    driver = webdriver.Firefox(options=options)
    driver.get(base_url)

    # Click the year
    click_element_by_text(driver, next_needed_year, partial_match=True)

    # Click the month
    click_element_by_text(driver, next_needed_month_text, sleep_time=16, partial_match=True)

    available_links = find_links_matching_all(driver,  [f'{next_needed_month_text.lower()}',
                                                        f'{next_needed_year}'], without_domain=True)
    
    download_excel_files_from_url(available_links, folder_name, filename_from_headers=True)
    driver.close()
    return available_links

def download_mip():
     # Open in browser
    driver = webdriver.Firefox(options=options)
    driver.get(base_url)
    # Click the year
    click_element_by_text(driver, next_needed_year + " - Nómina ")

    # Click the month
    click_element_by_text(driver, next_needed_month_text + " " + next_needed_year + " - Nómina")

    # Find the link to the Excel file
    content = driver.page_source
    excel_links = find_links_to_excel_files(content, domain="https://mip.gob.do")
    print(excel_links)

    # Download the Excel file
    download_excel_files_from_url(excel_links, folder_name)
    driver.close()
    return excel_links


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