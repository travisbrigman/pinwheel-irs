#importing requests, BeautifulSoup, pandas, csv
import bs4
from bs4 import BeautifulSoup
import requests
import pandas
from pandas import DataFrame
import csv
#command to create a structure of csv file in which we will populate our scraped data
with open('Opencodez_Articles.csv', mode='w') as csv_file:
   fieldnames = ['Link', 'Title', 'Para', 'Author', 'Date']
   writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
   writer.writeheader()
#Creating an empty lists of variables
article_link = []
article_title = []
article_para = []
article_author = []
article_date = []
#Defining the opencodezscraping function
def opencodezscraping(webpage, page_number):
   next_page = webpage + str(page_number)
   response= requests.get(str(next_page))
   soup = BeautifulSoup(response.content,"html.parser")
   soup_title= soup.findAll("h2",{"class":"title"})
   soup_para= soup.findAll("div",{"class":"post-content image-caption-format-1"})
   soup_date= soup.findAll("span",{"class":"thetime"})
   for x in range(len(soup_title)):
      article_author.append(soup_para[x].a.text.strip())
      article_date.append(soup_date[x].text.strip())
      article_link.append(soup_title[x].a['href'])
      article_title.append(soup_title[x].a['title'])
      article_para.append(soup_para[x].p.text.strip())
   #Generating the next page url
   if page_number < 16:
      page_number = page_number + 1
      opencodezscraping(webpage, page_number)
   #calling the function with relevant parameters
   opencodezscraping('https://www.opencodez.com/page/', 0)
   
   #creating the data frame and populating its data into the csv file
data = { 'Article_Link': article_link,
'Article_Title':article_title, 'Article_Para':article_para, 'Article_Author':article_author, 'Article_Date':article_date}
df = DataFrame(data, columns = ['Article_Link','Article_Title','Article_Para','Article_Author','Article_Date'])
df.to_csv(r'C:\Users\**\**\OpenCodez_Articles.csv')