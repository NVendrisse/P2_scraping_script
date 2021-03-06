from genericpath import exists
import shutil
import sys
import requests
from bs4 import BeautifulSoup
import urllib.request
import os


# Initiate global variable
file_encoding = "ansi"
url = "http://books.toscrape.com/index.html"
data_dir = "ScrapedData"
image_dir = "ScrapedImages"
index_request = requests.get(url)
csv_column_title = ["product_page_url", "universal_product_code", "title", "price_including_tax", "price_excluding_tax",
                    "number_available", "product_description", "category", "review_rating", "image_url"]
converter_dict = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
# Testing if the saving directories already exist, deleting them if True
if exists(data_dir):
    shutil.rmtree(data_dir)
if exists(image_dir):
    shutil.rmtree(image_dir)
# Creating directories for saving data
os.makedirs(data_dir, exist_ok=False)
os.makedirs(image_dir, exist_ok=False)
# Collecting all categories names and links
if index_request.ok:
    site_soup = BeautifulSoup(index_request.content, "html.parser")
    categories_links = site_soup.find(
        "div", class_="side_categories").find_all("a")
    categories_urls = []  # list of all categories urls
    categories_names = []  # list of all categories names
    for extracted_link in categories_links:
        categories_urls.append(
            "http://books.toscrape.com/{}".format(extracted_link["href"]))
        categories_names.append(extracted_link.text.strip())
# Collecting all products urls
for category_url in categories_urls[1:]:
    category_name = categories_names[categories_urls.index(category_url)]
    # Creating the csv file for the category
    with open("{}\\{}.csv".format(data_dir, category_name), "w", encoding=file_encoding, errors="ignore") as csv_file:
        csv_file.write(";".join(csv_column_title)+"\n")
    print("\tScraping category <{}>".format(category_name))
    category_request = requests.get(category_url)
    if category_request.ok:
        category_soup = BeautifulSoup(category_request.content, "html.parser")
        products_links = category_soup.find("ol", class_="row").find_all("a")
        pager_item = category_soup.find("ul", class_="pager")
        #Testing section for multipage
        if pager_item != None:
            next_page_url = pager_item.find("li", class_="next")
            while next_page_url != None:
                next_page = next_page_url.find("a")
                next_url = category_url.replace(
                    "index.html", next_page["href"])
                next_page_request = requests.get(next_url)
                if next_page_request.ok:
                    n_soup = BeautifulSoup(
                        next_page_request.content, "html.parser")
                    n_products_links = n_soup.find(
                        "ol", class_="row").find_all("a")
                    products_links.extend(n_products_links)
                next_page_url = n_soup.find("li", class_="next")
        products_urls = []  # list of all products url in the category
        for link in products_links:
            if link.parent.name == "div":
                products_urls.append(link["href"].replace(
                    "../../../", "http://books.toscrape.com/catalogue/"))
        for url in products_urls:
            urls_count = len(products_urls)
            current_progress = products_urls.index(url)
            progress_percent = int(((current_progress+1)/urls_count)*100)
            product_request = requests.get(url)
            if product_request.ok:
                # extracting the data
                product_soup = BeautifulSoup(
                    product_request.content, "html.parser")
                product_title = product_soup.find("h1").text  # title
                raw_product_informations = product_soup.find(
                    "table", class_="table table-striped").find_all("td")
                upc = raw_product_informations[0].text
                price_incl_tax = raw_product_informations[3].text
                price_excl_tax = raw_product_informations[2].text
                number_available = raw_product_informations[5].text.replace(
                    'In stock (', '').replace('available)', '')
                description = product_soup.find(
                    "article").find_all("p")[3].text.strip()
                raw_product_rating = product_soup.find(
                    "p", class_="star-rating")
                product_rating = "{} out of 5".format(
                    converter_dict[raw_product_rating["class"][1]])
                raw_image_url = product_soup.find(
                    "div", class_="item active").find_next("img")
                image_url = raw_image_url["src"].replace(
                    "../..", "http://books.toscrape.com")
                #Writing the data in csv file
                data_table = [url, upc, product_title, price_incl_tax, price_excl_tax,
                              number_available, description, category_name, product_rating, image_url]
                for i in range(0, len(data_table)):
                    data_table[i] = data_table[i].replace(";", ":")
                with open("{}\\{}.csv".format(data_dir, category_name), "a", encoding=file_encoding, errors="ignore") as csv_file:
                    csv_file.write(";".join(data_table)+"\n")
                #Formating product title to use as image filename
                for sp_char in ["\\", "/", ":", "?", "\"", "<", ">", "|", "*"]:
                    product_title = product_title.replace(sp_char, " ")
                #creating save path
                save_path = "{}\{}\{}".format(
                    os.getcwd(), image_dir, product_title)
                #Formating save path 
                if len(save_path) >= 255:
                    save_path = save_path[:250]
                if exists(save_path+".jpg"):
                    save_path += " (1)"
                #Downloading image
                urllib.request.urlretrieve(
                    image_url, "{}.jpg".format(save_path))

            print("Retrieving {} product{} : {}%".format(urls_count,"s" if urls_count>1 else "",progress_percent), end="\r")
        print()
