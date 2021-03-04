import requests
from bs4 import BeautifulSoup
import json
from operator import itemgetter

def fetchHTML(row_index, search_query):
    url_query = search_query.replace(" ", "+")
    URL = f'https://apps.irs.gov/app/picklist/list/priorFormPublication.html?resultsPerPage=200&sortColumn=sortOrder&indexOfFirstRow={str(row_index)}&criteria=formNumber&value={url_query}&isDescending=false'
    
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser') 

    return soup  

def prepHTML(fetched_html):
    table_body_results = fetched_html.find(id='picklistContentPane')
    page_number = fetched_html.find('th', class_='ShowByColumn')
    print(page_number)

    if page_number is not None:
        clean_pages = page_number.text.strip()
    else:
        print("query not found")
        
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
    Query_results = []

    if len(parsed_data) is not None:
        for entry in parsed_data:
            if entry["form_number"].upper() == query_term.upper():
                Query_results.append(entry)
            else:
                print(f"error - {entry} doesn't match query {query_term}")
    if len(Query_results) != 0:
        sorted_query_results = sorted(Query_results, key=itemgetter('year'))

        form_number = sorted_query_results[0]["form_number"]
        form_title = sorted_query_results[0]["form_title"]
        min_year = sorted_query_results[0]["year"]
        max_year= sorted_query_results[-1]["year"]

        sorted_result = {"form_number": form_number, "form_title": form_title, "min_year": min_year, "max_year": max_year}

        sorted_list = []
        sorted_list.append(sorted_result)
    else:
        print("no items matched the query")
    return sorted_list

def convert_to_json(managed_list):
    json_results = json.dumps(managed_list)
    print(json_results)


page_index = 0
search_query = ["Form W-2", "Form 11-C", "Form 1095-C"]

for term in search_query:
    parsed_html = []

    html = fetchHTML(page_index, term)

    table_body_results, page_numbers = prepHTML(html)
    parsed_markup = parseHTML(table_body_results)
    if page_numbers[1] < page_numbers[2]:
        page_index += 200
    parsed_html.extend(parsed_markup)
    sorted_data = sort_data(parsed_markup, term)
    json_conversion = convert_to_json(sorted_data)