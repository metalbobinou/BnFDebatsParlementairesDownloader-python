# Files
import sys
import os
from io import StringIO, BytesIO

# Regexp
import re

# Date
import datetime

# HTTP & URL
import urllib.request

# Beautiful Soup
from bs4 import BeautifulSoup

# Selenium [web browser for JS in code]
from selenium import webdriver
#from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

# Selenium Chromium
#from selenium.webdriver.chrome.options import Options

# Selelnium Firefox
from selenium.webdriver.firefox.options import Options

# Selenium exceptions
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException



### Contains small tools for dates and others
import MyCommonTools

###########################################################################################
## The objective of this module is to fetch the Ark ID of each document on the same date ##
###########################################################################################
##
## For example, from this URL :
# url = "https://gallica.bnf.fr/ark:/12148/cb328020951/date18900701"
## we can find these documents :
# url_res[0] = "https://gallica.bnf.fr/ark:/12148/bpt6k6296564p?rk=21459;2"
# url_res[1] = "https://gallica.bnf.fr/ark:/12148/bpt6k6457425x?rk=42918;4"
## but in some cases, it's the same document scanned differently......
## ...anyway : a human MUST check again these documents after.
# url = "https://gallica.bnf.fr/ark:/12148/cb371291967/date19400101"
##
##############################################################################

# File containing the last line read
g_file_last_line_name = "__last_multiple_document_checked.cache"

# File with double resolved URL
prefix_double_resolved_file_name = "resolved-bis_"

# File with undownloaded URL
prefix_unresolved_file_name = "unresolved-bis_"

### Small tools

# Remove the "?" suffix if it exists
def remove_suffix_question_from_url(url):
    match = re.search('\?.*$', url)
    # if no "?" found, let's send back the URL
    if (match == None):
        return (url)

    # if "?" found, let's remove it
    no_question_url = url[:match.start(0)]
    return (no_question_url)

# Remove the ".item" suffix if it exists
def remove_suffix_item_from_url(url):
    match = re.search('\.item$', url)
    # if no ".item" found, let's send back the URL
    if (match == None):
        return (url)

    # if ".item" found, let's remove it
    no_item_url = url[:match.start(0)]
    return (no_item_url)

# Remove the http[s]://gallica.bnf.fr/ark: prefix in a URL
def remove_prefix_https_from_url(url):
    match = re.search('^https?://gallica\.bnf\.fr/ark:', url)
    # if no prefix found, let's send back the URL
    if (match == None):
        return (url)

    # if prefix is found, let's keep only the ark id following it
    ark_id = url[match.end(0):]
    return (ark_id)

# Extract the Ark ID from a URL
def extract_ark_id_from_url(url):
    url_no_question = remove_suffix_question_from_url(url)
    url_no_suffix = remove_suffix_item_from_url(url_no_question)
    url_cleaned = remove_prefix_https_from_url(url_no_suffix)
    return (url_cleaned)


# Add a URL to the unresolved log
def update_file_unresolved_log(msg):
    ark_id_filename_input = os.path.basename(sys.argv[1])
    unresolved_filename = prefix_unresolved_file_name + ark_id_filename_input
    MyCommonTools.update_file_ouput(msg, unresolved_filename)


# Get the web page
def get_web_page(url):
    links = []
    print("## Checking URL : " + str(url))

    # Open a browser without GUI/in a terminal
    try:
        ## Chromium & Force size 1
        #options1 = Options()
        #options1.add_argument("window-size=500,300")
        #driver = webdriver.Chrome(chrome_options=options1)
        ## Chromium & No GUI
        #options = webdriver.ChromeOptions()
        #options.add_argument("--headless")
        #driver = webdriver.Chrome(options=options)
        ## Firefox & No GUI
        options = Options()
        options.add_argument("--headless")
        driver = webdriver.Firefox(options=options)
        ## Force size 2
        #driver.set_window_size(500, 300)
        #size = driver.get_window_size()

    # Failure in opening
    except (NoSuchElementException, WebDriverException) as e:
        print("### WEBDRIVER ERROR WHILE OPENING BROWSER:")
        print(str(e))
        print("#############")
        return (None)

    # All other exceptions
    except Exception as e:
        print("### UNKNOWN ERROR WHILE OPENING BROWSER:")
        print(str(e))
        print("#############")
        return (None)


    # Open the webpage
    try:
        driver.get(url)

    # If server is not responding
    except (NoSuchElementException, WebDriverException) as e:
        print("### WEBDRIVER ERROR WHEN REACHING URL:")
        print(str(e))
        print("#############")
        driver.quit()
        return (None)

    # All other exceptions
    except Exception as e:
        print("### UNKNOWN ERROR WHEN REACHING URL:")
        print(str(e))
        print("#############")
        driver.quit()
        return (None)

    ## Save the full page
    f = open("file.htm", "w")
    html = driver.page_source
    f.write(html)
    f.close

    ## Goto the results list : <div class="liste-resultats">
    div_liste_resultats = driver.find_element(By.CLASS_NAME, "liste-resultats")

    ## Extract all the results ID : <div class="resultat-id" id="resultat-id-X">
    ##  (where X is a number)
    div_resultats_ids = div_liste_resultats.find_elements(By.CLASS_NAME, "resultat-id")
    liste_id = []
    for element in div_resultats_ids:
        div_id = element.get_attribute("id")
        #html = div_liste_resultats.get_attribute('innerHTML')
        #print(html.strip())
        liste_id.append(div_id)
    nb_results = len(liste_id)

    ## Extract all the links to the documents
    divs_contenus = div_liste_resultats.find_elements(By.CLASS_NAME, "result-contenu")
    i = 1
    for div_contenu in divs_contenus:
        html = div_contenu.get_attribute('innerHTML')
        #print(html.strip())
        #print("#####")

        soup = BeautifulSoup(html.strip(), 'lxml')

        ## Get ID result
        divs = soup.div
        div_next = divs.find_next_sibling("div")
        id_tag = div_next['data-resultat-id']
        #print(str(id_tag))

        ## Get A HREF link
        a_href = soup.find("a").get("href")
        print(str(a_href))
        links.append(a_href)

        print("##########")
        i += 1

    ## Close one tab
    #driver.close()
    ## Close the full browser
    driver.quit()

    return (links)

# For each line, get the web page and process each result-id
def process_lines(lines):
    url_filename_input = os.path.basename(sys.argv[1])

    # File has been read and is in memory, everything is fine
    cur_line = 0
    max_line = len(lines)
    ## Open the temporary file for last processed line
    if (os.path.isfile(g_file_last_line_name)):
        fd = open(g_file_last_line_name, "r")
        file_last_line = fd.read()
        fd.close()
        cur_line = int(file_last_line)

    ## Update the unresolved log for saying an instance has been launched
    now = datetime.datetime.now()
    update_file_unresolved_log("# Launching URL multiple docs getter at " +
                               now.strftime("%d/%m/%Y %H:%M:%S"))
    # Continue the process of the file from the last state
    url_resolved_filename = prefix_double_resolved_file_name + url_filename_input
    while (cur_line != max_line):
        #url = lines[cur_line]
        ### Manages file with 2 columns
        line = lines[cur_line]
        line_split = re.split(" ", line)
        date = line_split[0]
        url = line_split[1]
        ###

        ## Get URLs in the page
        URLs = get_web_page(url)

        if (URLs is None):
            MyCommonTools.update_file_last_line(cur_line,
                                                g_file_last_line_name)
            print("ERROR: Failed at line " + str(cur_line))
            print("DATE : " + date)
            print("URL : " + url)
            return (-3)

        ## Write down the URLs
        i = 1
        for new_url in URLs:
            ark_id = extract_ark_id_from_url(new_url)
            line_resolved = date + "-" + str(i) + " " + ark_id
            MyCommonTools.update_file_ouput(line_resolved, url_resolved_filename)
            i += 1
        ###
        print("#############################################################")
        # read next line
        cur_line += 1

    # If everything ended well, let's remove the cache file with last state
    if (os.path.exists(g_file_last_line_name)):
        os.remove(g_file_last_line_name)
    # And let's rename the final double resolved list by adding a "_FINAL" inside
    if (os.path.exists(url_resolved_filename)):
        url_resolved_filename_final = os.path.splitext(url_resolved_filename)[0]
        url_resolved_filename_final = url_resolved_filename_final + "_final.txt"
        os.rename(url_resolved_filename, url_resolved_filename_final)
    else:
        print("--no doubleresolved file were created during this script--")

    return (0)

# Check for arguments in the CLI
def main():
    # Check for missing arguments
    if (len(sys.argv) != 2):
        print("Missing parameters")
        print("")
        print("Usage: " + sys.argv[0] + " list_of_URLs")
        print("")
        print("File list_of_URLs format: [one URL per line]")
        print("[date] [URL]")
        print("date : YYYY-MM-DD     URL : https://gallica.bnf.fr/ark:/...")
        exit(-1)
    else:
        url_filename_input = sys.argv[1]
        # Check if file is readable
        try:
            with open(url_filename_input) as fd:
                ## Put the whole file in memory in a list
                lines = [line.rstrip() for line in fd]
                #### OR ####
                ## Read and process file line by line (one read per line)
                #for line in fd:
                #    print(line.rstrip())

        # If file is unreadable, let's manage the exception
        except IOError:
            print("File " + url_file_input + " must exist and be readable")
            print("")
            print("Usage: " + sys.argv[0] + " list_of_URLs")
            print("")
            print("File list_of_URLs format: [one URL per line]")
            print("[date] [URL]")
            print("date : YYYY-MM-DD     URL : https://gallica.bnf.fr/ark:/...")
            exit(-2)

	# In other case, when evrything is fine, let's process lines
        ret = process_lines(lines)

        exit(ret)

main()
