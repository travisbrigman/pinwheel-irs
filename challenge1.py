import requests
from bs4 import BeautifulSoup
import json
from operator import itemgetter

query = ["Form W-2", "Form 11-C", "Form 1095-C"]
url_query = query.replace(" ", "+")
first_row_index = 0
page_numbers = [1, 0, 200]
Prior_year_product_data = []

while page_numbers[1] < page_numbers[2]:
    URL = f'https://apps.irs.gov/app/picklist/list/priorFormPublication.html?resultsPerPage=200&sortColumn=sortOrder&indexOfFirstRow={str(first_row_index)}&criteria=formNumber&value={url_query}&isDescending=false'
    
    page = requests.get(URL)

    soup = BeautifulSoup(page.content, 'html.parser')

    results = soup.find(id='picklistContentPane')
    page_view = soup.find('th', class_='ShowByColumn')

    if page_view.text is not None:
        clean_pages = page_view.text.strip()
    else:
        print("query not found")
    if clean_pages.__contains__(","):
        comma_killer = clean_pages.replace(",", "")
        page_numbers = [int(i) for i in comma_killer.split() if i.isdigit()] 
    else:
        page_numbers = [int(i) for i in clean_pages.split() if i.isdigit()] 
    
    table_elems = results.find_all('tr', class_=['odd','even'])

    for table_elem in table_elems:
        product_elem = table_elem.find('td', class_='LeftCellSpacer')
        title_elem = table_elem.find('td', class_='MiddleCellSpacer')
        date_elem = table_elem.find('td', class_='EndCellSpacer')

        form = product_elem.text.strip()
        title = title_elem.text.strip()
        year = date_elem.text.strip()

        entry = {"form_number": form, "form_title": title, "year": year}
        Prior_year_product_data.append(entry)

    first_row_index += 200

Query_results = []

if len(Prior_year_product_data) is not None:
    for entry in Prior_year_product_data:
        if entry["form_number"].upper() == query.upper():
            Query_results.append(entry)
        else:
            print(f"error - {entry} doesn't match query {query}")
if len(Query_results) != 0:
    sorted_query_results = sorted(Query_results, key=itemgetter('year'))

    form_number = sorted_query_results[0]["form_number"]
    form_title = sorted_query_results[0]["form_title"]
    min_year = sorted_query_results[0]["year"]
    max_year= sorted_query_results[-1]["year"]

    end_result = {"form_number": form_number, "form_title": form_title, "min_year": min_year, "max_year": max_year}

    end_list = []
    end_list.append(end_result)
    json_results = json.dumps(end_list)
    print(json_results)

else:
    print("no items matched the query")

