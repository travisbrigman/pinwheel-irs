import argparse
import re
from .functions import string_to_list, fetchHTML, prepHTML, parseHTML, sort_data, make_pdf_list, download_pdfs, convert_to_json

# COMMAND-LINE INTERFACE STUFF
# ----------------------------------------------------------------------------

years = []
for year in range(1912, 2022):
    years.append(year)
    year+=1

def valid_type(arg_value, pat=re.compile(r"[\w\s,-]")):
    if not pat.match(arg_value):
        raise argparse.ArgumentTypeError("must be valid format")
    return arg_value

my_parser = argparse.ArgumentParser(
    prog="pinwheel-irs-JSON", description="returns json results of irs forms site scrape"
)
my_parser.add_argument(
    "-forms_info", metavar="forms_info", type=valid_type, help="comma seperated string of forms"
)
my_parser.add_argument(
    "-forms_download", metavar="forms_download", type=valid_type, help="single case-insensitive search term"
)
my_parser.add_argument(
    "-min_year", metavar="min_year", type=int, help="the minimum year", choices = years
)
my_parser.add_argument(
    "-max_year", metavar="max_year", type=int, help="the maximum year", choices= years
)

args = my_parser.parse_args()
forms_info = args.forms_info
forms_download = args.forms_download
min_year = args.min_year
max_year = args.max_year

def string_to_list(form_string):
    if form_string.find(",") > -1:
        word_list = list(form_string.split(","))
    else:
        word_list = []
        word_list.append(form_string)

    form_list = []
    for string in word_list:
        string.strip()
        form_list.append(string)

    return form_list

if forms_info:
    search_query = string_to_list(forms_info)
elif (forms_download, min_year, max_year):
    search_query = string_to_list(forms_download)

# ----------------------------------------------------------------------------
#TODO: refactor argparse arguments
#TODO: Help info for CLI
#TODO: Readme.txt (maybe .md too?)
#TODO: test transmitting and setting up
#TODO: REGEX for Command Line??
def main():
    '''main entry point for the script.'''
    parsed_html = []
    for term in search_query:
        page_index = 0
        page_list = [0, 0, 1]
        try:
            while page_list[1] < page_list[2]:
                html = fetchHTML(page_index, term)
                table_body_results, page_numbers = prepHTML(html)
                page_list = page_numbers
                parsed_markup = parseHTML(table_body_results)
                parsed_html.extend(parsed_markup)
                page_index += 200

            # assert(len(page_list) > 0), "problems"

            sorted_data, filtered_list = sort_data(parsed_html, search_query)
            if search_query:
                json_conversion = convert_to_json(sorted_data)
            elif (search_query, min_year, max_year):
                pdfs = make_pdf_list(filtered_list, min_year, max_year)
                download_pdfs(pdfs)
    
        except(IndexError):
            print("couldn't find anything matching the search_query")