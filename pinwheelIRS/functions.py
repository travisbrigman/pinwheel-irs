import requests
from bs4 import BeautifulSoup
import json
from operator import itemgetter
import urllib.request
import os
import re

def string_to_list(form_string):
    '''
    convert string ex: "Form 11-C,Form W-2,Form 1095-C" to list.
    Parameters: form_string (string): a string value either with ',' or without.
    returns: form_list (list): a list of at least one value
    '''
    if form_string.find(",") > -1:
        form_list = list(form_string.split(","))
    else:
        form_list = []
        form_list.append(form_string)
    return form_list

def fetchHTML(row_index, search_query):
    '''
    gets HTML from site.
        Parameters: 
            row_index (int): integer to be passed into URL
            search_query (string): single search term to b passed into URL
        Returns:
            soup (BeautifulSoup): HTML results from URL    
    '''
    url_query = search_query.replace(" ", "+")
    URL = f'https://apps.irs.gov/app/picklist/list/priorFormPublication.html?resultsPerPage=200&sortColumn=sortOrder&indexOfFirstRow={str(row_index)}&criteria=formNumber&value={url_query}&isDescending=false'
    
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser') 

    return soup  

def prepHTML(fetched_html):
    '''
    Takes raw scraped HTML and prepares it to be manipulated.
        Parameters:
            fetched_html (BeautifulSoup): HTML object of type BeautifulSoup
        Returns:
            table_body_results (soup): An object of HTML from a section of the page that was scraped.
            page_numbers (list): a list containing 3 integers.
                                [0] is lowest result number on page
                                [1] is highsest number result on page
                                [2] is total results for search_query
    '''
    table_body_results = fetched_html.find(id='picklistContentPane')
    page_number = fetched_html.find('th', class_='ShowByColumn')

    clean_pages = ""
    if page_number is not None:
        clean_pages = page_number.text.strip()
    else:
        print("page_numbers not found")

    if clean_pages.__contains__(","):
        comma_killer = clean_pages.replace(",", "")
        page_numbers = [int(i) for i in comma_killer.split() if i.isdigit()] 
    else:
        page_numbers = [int(i) for i in clean_pages.split() if i.isdigit()] 

    return table_body_results, page_numbers

def parseHTML(prepped_results):
    '''
    Iterates through HTML and extracts matching data points and creates a list of dictionaries containing those data points.
    Parameters:
        prepped_results (soup): An object of HTML from a section of the page that was scraped.
    Returns:
        Prior_year_product_data (list): List of dictionaires containing:
                                            form_number ex: 'Form W-2'
                                            form_title ex: 'Wage and Tax Statement (Info Copy Only)'
                                            year: ex: 2019
                                            link: ex: https://www.irs.gov/pub/irs-prior/fw2--2019.pdf
    '''
    Prior_year_product_data = []

    table_elems = prepped_results.find_all('tr', class_=['odd','even'])

    for table_elem in table_elems:
        product_elem = table_elem.find('td', class_='LeftCellSpacer')
        product_link = table_elem.find('a')
        title_elem = table_elem.find('td', class_='MiddleCellSpacer')
        date_elem = table_elem.find('td', class_='EndCellSpacer')

        form = product_elem.text.strip()
        link = product_link.get('href')
        title = title_elem.text.strip()
        year = date_elem.text.strip()
        
        entry = {"form_number": form, "form_title": title, "year": year, "link": link}
        Prior_year_product_data.append(entry)
    
    return Prior_year_product_data

def sort_data(parsed_data, query_term):
    '''
    Sorts list of all dictionary items against a single query term.
        Parameters:
            parsed_data (list): list of dictionary items.
            query_term (string): single string item ex: 'Form 11-C"
        Returns:
            sorted_list (list): a list of dictionary items that summarizes the parsed_data list.
                                Dictionary contains:
                                form_number ex: 'Form 11-C'
                                form_title ex: 'Occupational Tax and Registration Return for Wagering'
                                min_year ex: 1974
                                max_year ex: 2017
            Query_results (list): a list of dictionary items that matched the query_term
    '''
    sorted_list = []

    for term in query_term:
        Query_results = []

        if len(parsed_data) is not None:
            for entry in parsed_data:
                if entry["form_number"].upper() == term.upper():
                    Query_results.append(entry)
                else:
                    print(f"error - {entry['form_number']} doesn't match query {term}")
        if len(Query_results) != 0:
            sorted_query_results = sorted(Query_results, key=itemgetter('year'))

            form_number = sorted_query_results[0]["form_number"]
            form_title = sorted_query_results[0]["form_title"]
            min_year = sorted_query_results[0]["year"]
            max_year= sorted_query_results[-1]["year"]

            sorted_result = {"form_number": form_number, "form_title": form_title, "min_year": min_year, "max_year": max_year}
            sorted_list.append(sorted_result)
        else:
            print("no items matched the query")
    return sorted_list, Query_results

def make_pdf_list(matching_term_list, min_year, max_year):
    '''
    creates a list of PDF's to be downloaded.
        Parameters:
            matching_term_list (list): a list of dictionary items that matched the query_term
            min_year (int): The lowest year to year the user wants results for.
            max_year (int): The highest, or most recent, year the user wants results for.
        Returns:
            items_to_download (list): a list of query matched dictionary items filtered against a range of years.
    '''
    year_list = []
    items_to_download = []
    if matching_term_list:
        for year in range(int(min_year) - 1, int(max_year)):
            year_list.append(year + 1)
            for list_item in matching_term_list:
                for form_year in year_list:
                    if list_item["year"] == str(form_year):
                        items_to_download.append(list_item)
    else:
        print("no items in the list match the year range")
    return items_to_download

def download_pdfs(list_of_pdfs):
    '''
    creates a sub-directory and downloads PDF's to that sub-directory.
        Parameters:
            list_of_pdfs (list): list of dictionary items matching search_query and year range.
    '''
    if list_of_pdfs:
        cwd = os.getcwd()
        directory = "pdfs"
        path = os.path.join(cwd, directory)
        
        try: 
            os.mkdir(path) 
        except OSError as error: 
            print(error)
        
        for item in list_of_pdfs:
            file_name = f"{item['form_number']}-{item['year']}.pdf"
            file_name_dir = os.path.join(path, file_name)
            url = item["link"]
            print('Beginning file download with urllib2...')

            urllib.request.urlretrieve(url, file_name_dir)
            

def convert_to_json(managed_list):
    '''
    Takes a summarized list of dictionary items and converts it to JSON.
    Gives the user the option to create a JSON file as well.
        Parameters:
            managed_list (list): a list of dictionary items that match search_query and express the min_year and max_year that query is available.
    '''
    json_results = json.dumps(managed_list, indent=1)
    print(json_results)
    while True:
        try:
            user_input_create_file = input("would you like to create a JSON file as well? (Y or N) ")
            re.match("^(?:Y|N)$", user_input_create_file)
            if user_input_create_file == "Y":
                with open('irs.json', 'w') as outfile:
                    json.dump(managed_list, outfile, indent=1)
                break
            elif user_input_create_file == "N":
                print("Ok, thanks running this script! 🐍")
                break
        except: 
            print("Error! Only Y or N allowed!")
