# P2_scraping_script
A scraping script in python that retrieve some books informations 
on the website books.toscrape.com and store them in a csv file.

## Installation :

Open your terminal in administrator mode and do the following steps :

**Windows user:**
```bash
cd ..\P2_scraping_script
python -m venv env
.\env\Scripts\activate
pip install -r requirements.txt
```

**MacOs or Linux user:**
```bash
cd ..\P2_scraping_script
python -m venv env
env/bin/activate
pip install -r requirements.txt
```

## Running the script
After installing the script, run it by using the command :
```bash
python P2_scraping_script.py
```
The process might take a while, and current progress is displayed

## Retrieving the scraped data
CSV files are encoded in ANSI to avoid some glitches with symbols

The script will automatically create two folders:
* ScrapedData for the csv files
* ScrapedImages for the extracted images

Those folders are deleted at the starting of the program if they already exists

## Author
Vendrisse Nicolas
