import requests
from bs4 import BeautifulSoup
import json
from operator import itemgetter
import argparse
import urllib.request
import os
import re

def fetchHTML(row_index, search_query):
    url_query = search_query.replace(" ", "+")
    URL = f'https://apps.irs.gov/app/picklist/list/priorFormPublication.html?resultsPerPage=200&sortColumn=sortOrder&indexOfFirstRow={str(row_index)}&criteria=formNumber&value={url_query}&isDescending=false'
    
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser') 

    return soup  

def prepHTML(fetched_html):
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
    json_results = json.dumps(managed_list, indent=1)
    print(json_results)
    user_input_create_file = input("would you like to create a JSON file as well? (Y or N) ")
    if not re.match("^(?:Y|N)$", user_input_create_file):
        print("Error! Only letters a-z allowed!")
    elif len(user_input_create_file) > 1:
        print("Error! Only Y or N allowed!")

    if user_input_create_file == "Y":
        with open('irs.json', 'w') as outfile:
            json.dump(managed_list, outfile, indent=1)
    elif user_input_create_file == "N":
        print("Ok, thanks running this script! 🐍")

def string_to_list(form_string):
    if form_string.find(",") > -1:
        form_list = list(form_string.split(","))
    else:
        form_list = []
        form_list.append(form_string)
    return form_list

# USE THE SCRIPT AS A COMMAND-LINE INTERFACE
# ----------------------------------------------------------------------------

    
years = set()
for year in range(1912, 2021):
    years.append(year)
    year+=1

my_parser = argparse.ArgumentParser(
    prog="pinwheel-irs-JSON", description="returns json results of irs forms site scrape"
)
my_parser.add_argument(
    "-forms_info", metavar="forms_info", type=str, help="comma seperated string of forms"
)
my_parser.add_argument(
    "-forms_download", metavar="forms_download", type=str, help="single case-insensitive search term"
)
my_parser.add_argument(
    "-min_year", metavar="min_year", type=str, help="the minimum year", choices = years
)
my_parser.add_argument(
    "-max_year", metavar="max_year", type=str, help="the maximum year", choices= years
)

args = my_parser.parse_args()
forms_info = args.forms_info
forms_download = args.forms_download
min_year = args.min_year
max_year = args.max_year

if forms_info:
    search_query = string_to_list(forms_info)
elif (forms_download, min_year, max_year):
    search_query = string_to_list(forms_download)

# ----------------------------------------------------------------------------
def main():
    parsed_html = []

    for term in search_query:
        page_index = 0
        page_list = [0, 0, 1]
        while page_list[1] < page_list[2]:
            html = fetchHTML(page_index, term)
            table_body_results, page_numbers = prepHTML(html)
            page_list = page_numbers
            parsed_markup = parseHTML(table_body_results)
            parsed_html.extend(parsed_markup)
            page_index += 200
    sorted_data, filtered_list = sort_data(parsed_html, search_query)
    if forms_info:
        json_conversion = convert_to_json(sorted_data)
    elif (forms_download, min_year, max_year):
        pdfs = make_pdf_list(filtered_list, min_year, max_year)
        download_pdfs(pdfs)


if __name__ == "__main__":
    main()
