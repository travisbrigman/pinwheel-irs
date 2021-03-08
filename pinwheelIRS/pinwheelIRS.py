'''
Runs the functions from function.py. Also sets up all the command line arguments

    Functions:
        valid_type
        string_to_list
        main       
'''

import argparse
import re

from .functions import fetchHTML, prepHTML, parseHTML, sort_data, make_pdf_list, download_pdfs, convert_to_json

# COMMAND-LINE INTERFACE STUFF
# ----------------------------------------------------------------------------

def valid_type(arg_value, pat=re.compile(r"[\w\s,-]")):
    if not pat.match(arg_value):
        raise argparse.ArgumentTypeError("must be valid format")
    return arg_value

my_parser = argparse.ArgumentParser(
    prog="pinwheel-irs-JSON", description="returns json results of irs forms site scrape"
)
my_group = my_parser.add_mutually_exclusive_group(required=True)
my_group.add_argument(
    "-info", metavar="FORMS INFO", type=valid_type, help="comma seperated string of forms"
)
my_group.add_argument(
    "-download", metavar="FORMS DOWNLOAD", type=valid_type, help="single case-insensitive search term"
)
my_parser.add_argument(
    "-years", metavar="MIN & MAX YEARS", type=int, help="the minimum and maximum years", choices=range(1912, 2022), nargs=2
)

args = my_parser.parse_args()
forms_info = args.info
forms_download = args.download
min_max_year = args.years

def string_to_list(form_string):
    if form_string.find(",") > -1:
        word_list = list(form_string.split(","))
    else:
        word_list = []
        word_list.append(form_string)

    form_list = []
    for string in word_list:
        stripped_word = string.strip()
        form_list.append(stripped_word)

    return form_list

if forms_info:
    search_query = string_to_list(forms_info)
elif (forms_download, min_max_year[0], min_max_year[1]):
    if min_max_year[0] < min_max_year[1]:
        search_query = string_to_list(forms_download)
    else:
        print("min year is more recent than max year")
        exit()
    if len(search_query) != 1:
        print("only one form type can be downloaded at a time")
        exit()

# ----------------------------------------------------------------------------
# TODO: Readme.txt (maybe .md too?)
# TODO: test transmitting and setting up
def main():
    """main entry point for the script."""
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
            sorted_data, filtered_list = sort_data(parsed_html, search_query)
        except IndexError:
            print("🤷🏻‍♂️couldn't find anything matching the search_query")
    try:
        if forms_info:
            convert_to_json(sorted_data)
        elif forms_download:
            pdfs = make_pdf_list(filtered_list, min_max_year[0], min_max_year[1])
            download_pdfs(pdfs)
    except:
        print("🤮bad things happen to good code")



