# File for common functions and variables used in the project
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import requests
import os
import re

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

def find_links_to_excel_files(content):
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
                ans.append(link_url)
    return list(set(ans))

def find_links_to_excel_files(content):
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
                ans.append(link_url)
    return list(set(ans))

def download_excel_files_from_url(excel_links, folder_name, filename_from_headers=None):
    for link in excel_links:
        print('Downloading Excel file:', link)
        # Create the folder if it doesn't exist
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        # Download the file
        r = requests.get(link, allow_redirects=True)
        # Get the filename from the URL
        if filename_from_headers is None:
            filename = re.findall(r'/([^/]+)$', link)[0]
        else:
            filename = r.headers.get('content-disposition').split('filename=')[1].replace('"','')
        
        if filename.endswith('.xls') or filename.endswith('.xlsx'):
            open(folder_name + '/' + filename, 'wb').write(r.content)
        else:
            print("File is not an Excel file:", filename)
