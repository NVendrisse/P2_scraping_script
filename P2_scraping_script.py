import requests
from bs4 import BeautifulSoup
import urllib.request
import os


# Initiate url and retrieving site data
url = "http://books.toscrape.com/index.html"
data_dir = ".\ScrapedData"
image_dir = ".\ScrapedImages"
index_request = requests.get(url)
csv_column_title = ["product_page_url", "universal_product_code", "title", "price_including_tax", "price_excluding_tax",
                    "number_available", "product_description", "category", "review_rating", "image_url"]
converter_dict = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
os.makedirs(data_dir, exist_ok=True)
os.makedirs(image_dir, exist_ok=True)
# Collecting all categories names and links
if index_request.ok:
    print("Extracting {} data".format(url))
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
    with open("{}\\{}.csv".format(data_dir, category_name), "w", encoding="utf-8") as csv_file:
        csv_file.write(";".join(csv_column_title)+"\n")
    print("\tScraping category <{}>".format(category_name))
    category_request = requests.get(category_url)
    if category_request.ok:
        category_soup = BeautifulSoup(category_request.content, "html.parser")
        products_links = category_soup.find("ol", class_="row").find_all("a")
        pager_item = category_soup.find("ul", class_="pager")
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
            product_request = requests.get(url)
            if product_request.ok:
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
                    "article").find_all("p")[3].text
                raw_product_rating = product_soup.find(
                    "p", class_="star-rating")
                product_rating = "{} / 5".format(
                    converter_dict[raw_product_rating["class"][1]])
                images_urls = []
                raw_image_url = product_soup.find(
                    "div", class_="item active").find_next("img")
                image_url = raw_image_url["src"].replace(
                    "../..", "http://books.toscrape.com")
                images_urls.append(image_url)
                data_table = [url, upc, product_title, price_incl_tax, price_excl_tax,
                              number_available, description, category_name, product_rating, image_url]
                for i in range(0, len(data_table)):
                    data_table[i] = data_table[i].replace(";", ":")
                with open("{}\\{}.csv".format(data_dir, category_name), "a", encoding="utf-8") as csv_file:
                    csv_file.write(";".join(data_table)+"\n")
                for sp_char in ["\\", "/", ":", "?", "\"", "<", ">", "|"]:
                    product_title = product_title.replace(sp_char, " ")
                product_title=product_title.replace(",","")
                if len("{}\{}.jpg".format(image_dir, product_title)) >= 255:
                    product_title = product_title[:240]
                print(product_title)
                urllib.request.urlretrieve(
                    image_url, "{}\{}.jpg".format(image_dir, product_title))
            print("{}/{}".format(current_progress+1, urls_count), end="\r")
        print()
