import requests
from bs4 import BeautifulSoup
import json
from operator import itemgetter
import argparse

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
        title_elem = table_elem.find('td', class_='MiddleCellSpacer')
        date_elem = table_elem.find('td', class_='EndCellSpacer')

        form = product_elem.text.strip()
        title = title_elem.text.strip()
        year = date_elem.text.strip()

        entry = {"form_number": form, "form_title": title, "year": year}
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
    return sorted_list

def convert_to_json(managed_list):
    json_results = json.dumps(managed_list, indent=1)
    print(json_results)


def string_to_list(form_string):
    
    form_list = list(form_string.split(","))
    return form_list

    # USE THE SCRIPT AS A COMMAND-LINE INTERFACE
# ----------------------------------------------------------------------------
my_parser = argparse.ArgumentParser(
    prog="pinwheel-irs-JSON", description="returns json results of irs forms site scrape"
)
my_parser.add_argument(
    "-forms", metavar="forms", type=str, help="comma seperated string of forms"
)

args = my_parser.parse_args()
forms = args.forms

search_query = string_to_list(forms)
# ----------------------------------------------------------------------------
# search_query = ["Form W-2", "Form 11-C", "Form 1095-C"]

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
sorted_data = sort_data(parsed_html, search_query)
json_conversion = convert_to_json(sorted_data)


