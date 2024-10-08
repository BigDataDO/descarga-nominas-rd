# File for common functions and variables used in the project
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import requests
import os
import re
import time
import zipfile

month_names_dict = {
    '01': 'Enero',
    '02': 'Febrero',
    '03': 'Marzo',
    '04': 'Abril',
    '05': 'Mayo',
    '06': 'Junio',
    '07': 'Julio',
    '08': 'Agosto',
    '09': 'Septiembre',
    '10': 'Octubre',
    '11': 'Noviembre',
    '12': 'Diciembre'
}


def click_element_by_text(driver, text, sleep_time=3, partial_match=False, list_match=False):
    """
    Clicks an element in the page by its text
    :param driver: Selenium driver
    :param text: text of the element to click
    :param sleep_time: time to wait after clicking
    :param partial_match: if True, will match the text partially
    :return: None
    """
    if partial_match:
        search_criteria = f"//*[contains(text(),'{text}')]"
    elif list_match:
        text_list = text.split(",")
        search_criteria = "|".join([f"//*[contains(text(), '{e}')]" for e in text_list])
    else:
        search_criteria = f"//*[text()='{text}']"
    date_elements = driver.find_elements(By.XPATH, search_criteria)
    # filter empty elements
    date_elements = [el for el in date_elements if el.text]
    date_elements[0].click()
    time.sleep(sleep_time)

def click_element_by_other_element(driver, text, element, sleep_time = 3):
    search_criteria = f"//*[contains(@{element},'{text}')]"
    date_elements = driver.find_elements(By.XPATH, search_criteria)  
    date_elements[0].click()
    time.sleep(sleep_time)          

def find_download_links(content, domain=None):
    """
    Finds all download links for Excel files in the content of a page
    :param content: HTML content of the page
    :param domain: Optional domain to prepend to the links if they're relative URLs
    :return: list of download links for Excel files
    """
    soup = BeautifulSoup(content, 'html.parser')
    download_link_tags = soup.find_all('a', class_='btn-descargar')
    download_links = []

    for tag in download_link_tags:
        if 'href' in tag.attrs:
            download_link = tag['href']
            # Prepend domain if provided and the link is relative
            if domain and not download_link.startswith(('http://', 'https://')):
                download_link = domain + download_link
            download_links.append(download_link)

    return download_links
    
def find_links_to_excel_files(content, domain=None):
    """
    Finds all links to Excel files in the content of a page
    :param content: HTML content of the page
    :return: list of links to Excel files
    """
    ans = []
    soup = BeautifulSoup(content, 'html.parser')
    a_tags = soup.find_all('a')
    for a in a_tags:
        # If the <a> tag has a href attribute
        if 'href' in a.attrs:
            link_url = a['href']

            # If the link is to an Excel file
            if (link_url.endswith('.xls') or link_url.endswith('.xlsx')) and (link_url not in ans):
                # Add the link to the list of Excel file links
                print('Found Excel file:', link_url)
                ans.append(domain+link_url if domain else link_url)
    return list(set(ans))

def find_links_matching_all(response, items, without_domain=False):
    """
    Finds all links in the response that contain all the items in the list
    :param response: Selenium driver or requests response
    :param items: list of strings to match
    :return: list of links
    """
    if isinstance(response, webdriver.firefox.webdriver.WebDriver):
        # For Selenium driver
        soup = BeautifulSoup(response.page_source, 'html.parser')
        current_url = response.current_url
    else:
        # For requests response
        soup = BeautifulSoup(response.content, 'html.parser')
        current_url = response.url
    domain = re.findall(r'^(https?://[^/]+)', current_url)[0]
    a_tags = soup.find_all('a')
    available_links = [a['href'] for a in a_tags if 'href' in a.attrs]
    matching_links = []
    for link in available_links:
        if all(item.upper() in link.upper() for item in items):
            matching_links.append(domain+link if without_domain is False else link)
    return list(set(matching_links))

def download_excel_files_from_url(excel_links, folder_name, filename_from_headers=None, headers=None, allow_redirects=True, split_arg = None):
    """
    Downloads all Excel files from a list of links
    :param excel_links: list of links to Excel files
    :param folder_name: folder to save the files
    :param filename_from_headers: if True, will get the filename from the headers instead of the URL
    :return: None
    Note: It only works if the link ends with .xls or .xlsx. For pages where a download button is clicked, 
    """
    for link in excel_links:
        print('Downloading Excel file:', link)
        # Create the folder if it doesn't exist
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        # Download the file
        r = requests.get(link, allow_redirects=allow_redirects, headers=headers,verify=False)
        # Get the filename from the URL

        # if the file is a PDF, skip it
        if 'application/pdf' in r.headers.get('content-type' or ''):
            print('PDF file found, skipping:', link)
            continue

        if filename_from_headers is None:
            filename = re.findall(r'/([^/]+)$', link)[0]
        else:
            if 'content-disposition' in r.headers:
                filename = r.headers.get('content-disposition').split('filename=')[1].replace('"','')
            elif not allow_redirects:
                filename = r.headers.get('location').split(split_arg)[1]
            ##elif 'officedocument' in r.headers.get('content-type'):
            ##    filename = re.findall(r'filename="([^"]+)"', r.headers.get('content-type'))[0]
            else:
                print('Could not find filename in headers, using URL')
                filename = re.findall(r'/([^/]+)$', link)[0]
        
        # make sure filename is a valid windows/linux filename
        filename = re.sub(r'[\\/*?:"<>=|]', '', filename)

        if not filename.endswith('.xls') and not filename.endswith('.xlsx'):
            filename += '.xlsx'
            
        open(folder_name + '/' + filename, 'wb').write(r.content)
        print("Decargado")

def download_zip_files_from_url(excel_links, folder_name, filename_from_headers=None, headers=None, allow_redirects=True, split_arg = None):
    
    for link in excel_links:
        print('Downloading Excel file:', link)
        # Create the folder if it doesn't exist
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        # Download the file
        r = requests.get(link, allow_redirects=allow_redirects, headers=headers,verify=False)
        # Get the filename from the URL

        # if the file is a PDF, skip it
        if 'application/pdf' in r.headers.get('content-type'):
            print('PDF file found, skipping:', link)
            continue

        if filename_from_headers is None:
            filename = re.findall(r'/([^/]+)$', link)[0]
        else:
            if 'content-disposition' in r.headers:
                filename = r.headers.get('content-disposition').split('filename=')[1].replace('"','')
            elif not allow_redirects:
                filename = r.headers.get('location').split(split_arg)[1]
            elif 'officedocument' in r.headers.get('content-type'):
                filename = re.findall(r'filename="([^"]+)"', r.headers.get('content-type'))[0]
            else:
                print('Could not find filename in headers, using URL')
                filename = re.findall(r'/([^/]+)$', link)[0]
        
        # make sure filename is a valid windows/linux filename
        filename = re.sub(r'[\\/*?:"<>=|]', '', filename)

        if not filename.endswith('.zip'):
            filename += '.zip'
            
        open(folder_name + '/' + filename, 'wb').write(r.content)
        with zipfile.ZipFile(folder_name + '/' + filename,'r') as zip_ref:
            ##zip_ref.extractall(folder_name)
            for file_info in zip_ref.infolist():
                if file_info.filename.endswith('.xlsx') or file_info.filename.endswith('.xls'):
                    zip_ref.extract(file_info, folder_name)
            zip_ref.close()
        print("Decargado")        