import requests
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

options = Options()
options.add_argument("--disable-notifications")
options.add_argument("--headless")
chrome = webdriver.Chrome('./chromedriver', options=options)
chrome.get("Your target website") # Use the website you want to scrape


# Login 
user_email = "" # Please use your own email
user_password = "" # Please use your own password

email = chrome.find_element_by_id("email") 
password = chrome.find_element_by_id("pass")

email.send_keys(user_email)
password.send_keys(user_password)
password.submit()

# Scrape the context you want

final_page_number = 30 # Relace this number to the final page number after you search for some keywords

for page in range(1, final_page_number):
    url = "https://xxxxxx" + str(page) + "xxxxxx" # Modify this depending on the website URL formate 
    req = requests.get(url)
    soup = BeautifulSoup(req.content, 'html.parser')

    mydivs = soup.findAll("div", {"class": "xxxxxxx"}) # Find the tags with specific class

    for div in mydivs:
        component_in_url = div.contents[1]["href"].split("/")
        urlArticle = "https://xxxxxx" + div.contents[1]["href"]
        reqArticle = requests.get(urlArticle)
        soupArticle = BeautifulSoup(reqArticle.content, "html.parser")
        contextArticle = soupArticle.find("article", {"class": "xxxxxxx"})
        all_p = contextArticle.contents[1].find_all("p")
        context = ""
        for p in all_p:
            context += str(p.text)

        with open("Your file name", "w") as file:
            file.write(context)
    print("Complete {}/{} pages".format(page, final_page_number))
