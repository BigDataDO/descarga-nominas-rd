from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import date
from datetime import datetime
import re
import requests
import pandas as pd
from utils import *
import time
import logging


#### Options ####
# Run browser with no window
CONF_HEADLESS_BROWSER = False
logging.basicConfig(filename='errors.log', filemode='w', level=logging.INFO)

# Reading Source files
url_sources = pd.read_csv('sources_list.csv')
df = pd.read_csv('input.csv')
df = pd.merge(df, url_sources, on='nombre_corto', how='left')

#### Processing Functions ####
# For each portal, we need to write a function that finds the files to download


def download_ce():
    # Open in browser
    driver = webdriver.Firefox(options=options)
    driver.get(base_url)
    # Click the year
    click_element_by_text(driver, next_needed_year)

    # Click the month
    click_element_by_text(driver, next_needed_month_text)

    # Find the link to the Excel file
    content = driver.page_source
    excel_links = find_download_links(content,'https://www.comedoreseconomicos.gob.do')

    # Download the Excel file
    download_excel_files_from_url(excel_links, folder_name)
    driver.close()
    return excel_links


def download_cgr():
    # Open in browser
    driver = webdriver.Firefox(options=options)
    driver.get(base_url)
    # Click the year
    click_element_by_text(driver, next_needed_year)

    # Click the month
    click_element_by_text(driver, next_needed_month_text)

    # Find the link to the Excel file
    content = driver.page_source
    excel_links = find_download_links(content,'https://www.contraloria.gob.do')


    # Download the Excel file
    download_excel_files_from_url(excel_links, folder_name)
    driver.close()
    return excel_links


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
    click_element_by_text(driver, f'{next_needed_month_text.upper()},{next_needed_month_text.lower()},{next_needed_month_text}', list_match=True)

    available_links = find_links_matching_all(driver,  [f'{next_needed_month_text.lower()}',
                                                        f'{next_needed_year}',
                                                        'download'])
    download_excel_files_from_url(available_links, folder_name, filename_from_headers=True)
    # Click Nominas Adicionales
    time.sleep(3)
    click_element_by_text(driver, 'NOMINAS ADICIONALES')

    available_links = find_links_matching_all(driver,  [f'{next_needed_month_text.lower()}',
                                                        f'{next_needed_year}',
                                                        'download'])

    download_excel_files_from_url(available_links, folder_name, filename_from_headers=True)
    driver.close()
    return available_links

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
    click_element_by_text(driver, f'Nominas de Empleados')
    # Click the year
    click_element_by_text(driver, next_needed_year, sleep_time=30)

    # Click the month
    click_element_by_text(driver, next_needed_month_text, sleep_time=30)

    #Click the nomina
    #click_element_by_text(driver, "Nómina Sueldos Fijos "+next_needed_month_text+"-"+next_needed_year, sleep_time=15)

    #available_links = find_links_matching_all(driver,  [f'{next_needed_month_text.lower()}',
    #                                                    f'{next_needed_year}',
    #                                                    'nomina-sueldos-fijos'], without_domain=True)

    available_links = find_links_to_excel_files(driver.page_source)

    # Download the Excel file
    download_excel_files_from_url(available_links, folder_name)
    driver.close()
    return available_links
        
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
    click_element_by_text(driver, next_needed_month_text, partial_match=True)

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
    time.sleep(3)

    # Find the link to the Excel file
    content = driver.page_source
    excel_links = find_links_to_excel_files(content)

    # Download the Excel file
    download_excel_files_from_url(excel_links, folder_name)
    driver.close()
    return excel_links

def download_omsa():
    driver = webdriver.Firefox(options=options)

    if int(next_needed_year) < 2024:
        list = [
            ' Nómina contratados', 'Nómina fija',
        ]

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

    else:
        driver.get(base_url)
        click_element_by_text(driver, "NOMINA GENERAL 2024")
        click_element_by_text(driver, "2024")

        available_links = find_links_matching_all(driver, [f'{next_needed_month_text.lower()}'], without_domain=False)

        download_excel_files_from_url(available_links, folder_name)

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
    time.sleep(3) 

    # Click the month
    if int(next_needed_year) < 2024:
        click_element_by_text(driver, next_needed_month_text + " " + next_needed_year + " - Nómina")
    else:
        click_element_by_text(driver, f"{next_needed_month_text} {next_needed_year} Nomina")

    time.sleep(3)    

    # Find the link to the Excel file
    content = driver.page_source
    excel_links = find_links_to_excel_files(content, domain="https://mip.gob.do")

    # Download the Excel file
    download_excel_files_from_url(excel_links, folder_name)
    driver.close()
    return excel_links

def download_pgr():
    # Open in headless browser
    driver = webdriver.Firefox(options=options)
    driver.get(base_url)

    # Click the year
    click_element_by_text(driver, next_needed_year, partial_match=True)

    # Click the month
    click_element_by_text(driver, next_needed_month_text, partial_match=True)

    available_links = find_links_matching_all(driver,  ['Inicio/DatosAbiertos'])

    download_excel_files_from_url(available_links, folder_name)
    driver.close()
    return available_links

def download_mt():
     # Open in browser
    driver = webdriver.Firefox(options=options)
    driver.get(base_url)
    # Click the year
    click_element_by_text(driver, "NOMINA "+next_needed_year)

    # Click the month
    click_element_by_text(driver, f"NOMINA DE EMPLEADOS - {next_needed_month_text.upper()} {next_needed_year}")

    # Find the link to the Excel file
    content = driver.page_source
    excel_links = find_links_to_excel_files(content, domain="https://mt.gob.do")

    # Download the Excel file
    download_excel_files_from_url(excel_links, folder_name)
    driver.close()
    return excel_links

def download_mimarena():
    list = [
        'Personal en Suplencia',
        'Personal Temporal',
        'Personal en Interinato',
        'Personal Militar',
        'Personal Fijo'
    ]

    # Open in browser
    driver = webdriver.Firefox(options=options)

    for item in list:
        print(item)
        driver.get(base_url)
        # Click the year
        click_element_by_text(driver, next_needed_year)

        # Click the month
        click_element_by_text(driver, next_needed_month_text)

        # Click the nomina
        click_element_by_text(driver, item)

        # Find the link to the Excel file
        content = driver.page_source
        excel_links = find_links_to_excel_files(content)

        # Download the Excel file
        download_excel_files_from_url(excel_links, folder_name)

    driver.close()
    return excel_links

def download_iad(): ##INSTITUTO AGRARIO DOMINICANO
    driver = webdriver.Firefox(options=options)
    driver.get(base_url)

    click_element_by_text(driver, 'Nomina Personal Fijo')
    click_element_by_text(driver, next_needed_year)
    click_element_by_text(driver, next_needed_month_text)

    content = driver.page_source
    ##excel_links = find_links_to_excel_files(content)
    excel_links = find_download_links(content,'https://iad.gob.do')

    ##Se necesita volver al inicio
    click_element_by_text(driver, 'Nómina ')
    click_element_by_text(driver, 'Nomina Personal Temporero')
    click_element_by_text(driver, next_needed_year)
    click_element_by_text(driver, next_needed_month_text)

    content = driver.page_source
    ##excel_links.extend(find_links_to_excel_files(content))
    excel_links.extend(find_download_links(content,'https://iad.gob.do'))

    download_excel_files_from_url(excel_links, folder_name)
    driver.close()

    return excel_links

def download_mh():
    driver = webdriver.Firefox(options=options)
    driver.get(base_url)

    click_element_by_text(driver, next_needed_year)
    ##click_element_by_text(driver, 'Ver Documentos', partial_match=True)

    
    ##x = driver.find_elements(By.XPATH, f"//*[contains(text(),'{next_needed_month_text}')]")
    ##click_element_by_text(x, 'Ver Documentos', partial_match=True)

    available_links = find_links_matching_all(driver,  [f'{next_needed_month_text.lower()}-{next_needed_year}','xls'], without_domain=True)
    download_excel_files_from_url(available_links, folder_name)
    driver.close()

    return available_links

def download_ln():
    driver = webdriver.Firefox(options=options)
    driver.get(base_url)

    click_element_by_text(driver, next_needed_year, partial_match=True)

    available_links = find_links_matching_all(driver,  [f'{next_needed_month_text.upper()}_{next_needed_year}','xlsx'], without_domain=True)
    download_excel_files_from_url(available_links, folder_name)
    driver.close()

    return available_links

def download_mivhed():
    listaCategorias = [
        'Nóminas Fijos',
        'Nóminas Pensionados',
        'Personal Contratados'
    ]

    driver = webdriver.Firefox(options=options)
    
    for categoria in listaCategorias:
        driver.get(base_url)
        click_element_by_text(driver, categoria)
        if next_needed_year != date.today().year:
            click_element_by_text(driver, f' {next_needed_year}',partial_match=True)
        available_links = find_links_matching_all(driver, [f'{next_needed_month_text}_{next_needed_year}','xlsx'], without_domain=False)            
        download_excel_files_from_url(available_links,folder_name)

    driver.close()
    return available_links

def download_mj():
    driver = webdriver.Firefox(options=options)
    driver.get(base_url)

    click_element_by_other_element(driver, f'nominas-de-empleados-{next_needed_year}', 'href')
    available_links = find_links_matching_all(driver, [f'{next_needed_month_text}-{next_needed_year}'], without_domain=True)
    download_excel_files_from_url(available_links,folder_name)

    driver.close()
    return available_links

def download_mispas():
    driver = webdriver.Firefox(options=options)
    ##driver.implicitly_wait(10);
    driver.get(base_url)

    click_element_by_text(driver,f'Año {next_needed_year}')
    click_element_by_text(driver,f'{next_needed_month_text}')

    available_links = find_links_to_excel_files(driver.page_source)
    download_excel_files_from_url(available_links,folder_name)

    driver.close()
    return available_links

def download_mepyd():
    driver = webdriver.Firefox(options=options)
    ##driver.implicitly_wait(10);
    driver.get(base_url)

    cat_list = ['Fijos', 'Vigilantes', 'Contratados temporeros', 'Caracter eventual']

    available_links = []

    for cat in cat_list:
        click_element_by_text(driver, f"{next_needed_month_text}")
        time.sleep(3)
        click_element_by_text(driver, cat)
        btn = driver.find_elements(By.XPATH, f"//*[contains(@class,'ext xlsx')]")  
        btn[0].find_element(By.XPATH, ".//a").click()
        time.sleep(3)
        available_links.extend(find_links_to_excel_files(driver.page_source))
        driver.get(base_url)
        time.sleep(3)

    download_excel_files_from_url(available_links,folder_name)

    driver.close()
    return available_links

def download_caasd():
    driver = webdriver.Firefox(options=options)
    driver.get(base_url)

    click_element_by_text(driver,f"Nomina de Empleados {next_needed_year} ")
    click_element_by_text(driver,f"Nomina de Empleados {next_needed_month_text} {next_needed_year} ")

    available_links = find_links_to_excel_files(driver.page_source)

    download_excel_files_from_url(available_links,folder_name)

    driver.close()
    return available_links

def download_indrhi():
    driver = webdriver.Firefox(options=options)
    carpetas = ['Nómina de Empleados Fijos',
                'Nóminas Contratados',
                'Nóminas Seguridad',
                'Nomina Jornaleros',
                'Jubilaciones, Pensiones y Retiros']
    
    available_links=[]

    for carpeta in carpetas:
        driver.get(base_url)
        click_element_by_text(driver,carpeta)
        ##driver.implicitly_wait(30)
        ##click_element_by_text(driver,f"{next_needed_year}",partial_match=True)
        WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH, f"//a[contains(@title,'Año {next_needed_year}')]")))

        ##WebDriverWait(driver,30).until(EC.((By.XPATH,f"//div[contains(@class, 'mediaTableWrapper')]")))

        time.sleep(10) ##No encontre otra forma de que se lograse el click

        driver.find_element(By.XPATH, f"//a[contains(@title,'{next_needed_year}')]").click()

        WebDriverWait(driver,10).until(EC.presence_of_all_elements_located((By.XPATH,f"//a[contains(@class, 'downloadlink')]")))

        ##WebDriverWait(driver,100).until(EC.)
        ##x = driver.find_element(By.XPATH,f"//a[contains(@title,'{next_needed_year}')]")
        
        available_links.extend(find_links_matching_all(driver, [f'{next_needed_month_text.lower()}'], without_domain=False))

    download_excel_files_from_url(available_links,folder_name)    

    driver.close()
    return available_links

def download_inespre():
    driver = webdriver.Firefox(options=options)
    driver.get(base_url)

    available_links = find_links_matching_all(driver, [f'{next_needed_month_text.lower()}-{next_needed_year}'], without_domain=True)

    download_excel_files_from_url(available_links,folder_name) 

    driver.close()
    return available_links

def download_mirex():
    driver = webdriver.Firefox(options=options)
    driver.get(base_url)

    btn = WebDriverWait(driver,10).until(
        EC.element_to_be_clickable((By.XPATH,f"//*[contains(@title,'{next_needed_year}')]"))
    )
    driver.execute_script("arguments[0].click();", btn)

    time.sleep(5)
    
    available_links = find_links_matching_all(driver,[f"{next_needed_month_text.upper()}",
                                                      f"{next_needed_year}",
                                                      f".zip"],
                                                      without_domain=True)
    
    download_zip_files_from_url(available_links, folder_name)

    driver.close()
    return available_links

def download_mem():
    driver = webdriver.Firefox(options=options)
    driver.get(base_url)    

    lista_links = driver.find_elements(By.XPATH, f"//*[contains(text(),'{next_needed_month_text}')]")
    lista_links[datetime.now().year - int(next_needed_year)].click()
    time.sleep(3)

    available_links = find_links_to_excel_files(driver.page_source,domain='https://transparencia.mem.gob.do')

    #boton_siguiente = driver.find_element(By.XPATH, f"//*[text()='Siguiente']")

    #while boton_siguiente is not None:
    #    boton_siguiente.click()
    #    time.sleep(3)
    #    available_links.extend(find_links_to_excel_files(driver.page_source))
    #    boton_siguiente = driver.find_element(By.XPATH, f"//*[text()='Siguiente']")

    download_excel_files_from_url(available_links,folder_name)

    driver.close()
    return available_links

def download_mapre():
    driver = webdriver.Firefox(options=options)
    driver.get(base_url)

    driver.find_element(By.XPATH,f"//*[text()='Ministerio Administrativo de la Presidencia (MAPRE)']").click()
    time.sleep(2)
    driver.find_element(By.XPATH,f"//*[text()='{next_needed_year}']").click()
    time.sleep(2)
    driver.find_element(By.XPATH,f"//*[text()='{next_needed_month_text}']").click()
    time.sleep(2)
    available_links = find_links_to_excel_files(driver.page_source)

    download_excel_files_from_url(available_links,folder_name)

    driver.close()
    return available_links

def download_minpre():
    #No se logra descargar con el proceso standard porque que el link es un ajax.php, 
    #entonces se tiene que hacer click y que se descargue en la carpeta por defecto del navegador
    options.set_preference("browser.download.folderList",2)
    options.set_preference("browser.download.manager.showWhenStarting", False)
    options.set_preference("browser.download.dir", folder_name)
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/xls")

    driver = webdriver.Firefox(options=options)
    driver.get(base_url)

    pages = ['mina PROETP',
             'mina de personal fijo',
             'mina de personal contratado']
    
    ##available_links = []

    for page in pages:
        time.sleep(10)
        #click_element_by_text(driver, f"{page} {next_needed_year}",partial_match=True)
        #click_element_by_text(driver, f"{next_needed_month_text}",partial_match=True)
        
        btn = WebDriverWait(driver,10).until(
            EC.element_to_be_clickable((By.XPATH,f"//*[contains(@title,'{page} {next_needed_year}')]"))
        )
        #btn.click()
        driver.execute_script("arguments[0].click();", btn)

        btn = WebDriverWait(driver,10).until(
            EC.element_to_be_clickable((By.XPATH,f"//*[contains(@title,'{next_needed_month_text}')]"))
        )
        #btn.click()
        driver.execute_script("arguments[0].click();", btn)

        ##available_links.extend(find_links_to_excel_files(driver.page_source))
        ##available_links = find_download_links(driver.page_source)
        ##available_links = find_links_matching_all(driver,f'xls',True)
        ##download_excel_files_from_url(available_links,folder_name)
        ##a = driver.find_element(By.XPATH,f"//a[contains(@title,'xls')]")
        ##link = a.get_attribute('href') 
        ##filename = a.get_attribute('data-name')
        ##r = requests.get(link, allow_redirects=True, headers=None,verify=False)
        ##open(folder_name + '/' + filename, 'wb').write(r.content)  

        time.sleep(5)

        driver.find_element(By.XPATH,f"//a[contains(@title,'xls')]").click()

        time.sleep(2)

        driver.find_element(By.XPATH,f"//*[contains(@title,'Carpeta superior')]").click()
        time.sleep(5)
        driver.find_element(By.XPATH,f"//*[contains(@title,'Carpeta superior')]").click()
        time.sleep(5)

    ##download_excel_files_from_url(available_links,folder_name)

    driver.close()
    return 1

def download_dgii():
    driver = webdriver.Firefox(options=options)
    driver.get(base_url)

    available_links = find_links_matching_all(driver,[f"{next_needed_month_text}",
                                                      f"{next_needed_year}",
                                                      f".zip"],
                                                      without_domain=False)

    download_zip_files_from_url(available_links,folder_name)

    driver.close()
    return available_links

def download_coraasan():
    # Open in browser
    driver = webdriver.Firefox(options=options)
    driver.get(base_url)
    # Click the year
    click_element_by_text(driver, f'Nómina {next_needed_year} (CORAASAN)')

    # Click folder
    click_element_by_text(driver, f'Nómina empleados fijos')

    excel_links = find_links_matching_all(driver
                                          ,[f'nomina-{next_needed_month_text.lower()}-{next_needed_year}'
                                          ,'xlsx'])
    download_excel_files_from_url(excel_links, folder_name, filename_from_headers=True)

    driver.close()
    return excel_links

def download_propeep():
    # Open in browser
    driver = webdriver.Firefox(options=options)
    driver.get( f'{base_url}/nonima-{next_needed_year}' )
    
    click_element_by_text(driver,next_needed_month_text)

    ##excel_links = find_links_matching_all(driver
    ##                                      ,[f'personal-fijo'
    ##                                      ,f'{next_needed_month_text.lower()}'
    ##                                      ,'xlsx'])

    excel_links = []
    btns = driver.find_elements(By.CLASS_NAME,'xlsx')
    for btn in btns:
        btn.find_element(By.TAG_NAME,'a').click()
        time.sleep(2)
        excel_links.extend(find_links_to_excel_files(driver.page_source))
        click_element_by_other_element(driver,'wpfd-close','class')
        time.sleep(2)

    download_excel_files_from_url(excel_links, folder_name)

    driver.close()
    return excel_links

def download_map():
    # Open in browser
    driver = webdriver.Firefox(options=options)
    driver.get(base_url)
    # Click the year
    click_element_by_text(driver, next_needed_year)

    # Click the month
    click_element_by_text(driver, next_needed_month_text)

    excel_links = find_links_matching_all(driver
                                          ,[f'empleados-fijo'
                                          ,f'{next_needed_year}'
                                          ,f'{next_needed_month_text.lower()}'
                                          ,'xlsx']
                                          ,True)
    download_excel_files_from_url(excel_links, folder_name, filename_from_headers=True)
    driver.close()
    return excel_links

def download_ma():
    # Open in browser
    driver = webdriver.Firefox(options=options)
    driver.get(base_url)
    # Click the year
    click_element_by_text(driver, next_needed_year,partial_match=True)

    # Click the month
    click_element_by_text(driver, next_needed_month_text,partial_match=True)

    subfolder = ['regional-central','regional-norte','sede-central']
    for folder in subfolder:
        #driver.get(f'{base_url}/{folder}')
        # Click the year
        click_element_by_text(driver, folder, partial_match=True)
        excel_links = find_links_matching_all(driver
                                            ,[f'{folder}'
                                            ,f'{next_needed_year}'
                                            ,f'{next_needed_month_text.lower()}'
                                            ,'xlsx']
                                            ,True)
        download_excel_files_from_url(excel_links, folder_name, filename_from_headers=True)
    driver.close()
    return excel_links

def download_minerd():
   # Open in browser
    driver = webdriver.Firefox(options=options)
    driver.get( f'{base_url}/{next_needed_year}/{next_needed_month_text}/listados' )

    excel_links = find_links_matching_all(driver
                                            ,[f'{next_needed_year}'
                                            ,f'{next_needed_month_text.lower()}'
                                            ,'xlsx']
                                            ,True)
    download_excel_files_from_url(excel_links, folder_name, filename_from_headers=True)

    driver.close()
    return excel_links

def download_mescyt():
   # Open in browser
    driver = webdriver.Firefox(options=options)
    driver.get( f'{base_url}/personal-fijo/' )

        # Click the year
    click_element_by_text(driver, next_needed_year)

    # Click the month
    click_element_by_text(driver, f'{next_needed_month} - {next_needed_month_text.lower()}')

    excel_links = find_links_matching_all(driver
                                            ,[f'{next_needed_year}'
                                            ,f'{next_needed_month_text.lower()}'
                                            ,'xlsx']
                                            ,True)
    download_excel_files_from_url(excel_links, folder_name, filename_from_headers=True)

    driver.close()
    return excel_links

def download_sb():
    # Open in browser
    driver = webdriver.Firefox(options=options)
    driver.get( f'{base_url}?anio={next_needed_year}&mes={next_needed_month_text}' )

    time.sleep(3)

    click_element_by_text(driver, f'{next_needed_month_text} {next_needed_year}')

    excel_links = find_links_matching_all(driver
                                            ,[f'{next_needed_year}'
                                            ,f'{next_needed_month_text.lower()}'
                                            ,'xlsx']
                                            )
    download_excel_files_from_url(excel_links, folder_name, filename_from_headers=True)

    driver.close()
    return excel_links

def download_superseguro():
    # Open in browser
    driver = webdriver.Firefox(options=options)
    driver.get(base_url)
    # Click the year
    click_element_by_text(driver, next_needed_year)

    # Click the month

    click_element_by_text(driver, next_needed_month_text)

    # Find the link to the Excel file
    excel_links = find_links_matching_all(driver
                                            ,[f'{next_needed_year}'
                                            ,f'{next_needed_month_text.lower()}'
                                            ,'xlsx']
                                            )
    download_excel_files_from_url(excel_links, folder_name, filename_from_headers=True)
    driver.close()
    return excel_links

# main function
if __name__ == "__main__":
    
    for i in range(len(df)):
        try:
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
        except Exception as e:
            logging.error(f'Error procesando {df['nombre_corto'][i]}', exc_info=True)
            continue    
