# Files
import sys
import os

# Regexp
import re

# Date
import datetime

# HTTP & URL
import urllib.request

# Selenium [web browser for JS in code]
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

# Selenium Chromium
#from selenium.webdriver.chrome.options import Options

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
## !!! WARNING !!!
##
## The first "f" is useless for progressing in the documents !
## Only the second one is important !!!
## For getting the page 2, you MUST access :                   v
##   https://gallica.bnf.fr/ark:/12148/bpt6k6494792j/f1.image/f2.jpeg
## or :
##   https://gallica.bnf.fr/ark:/12148/bpt6k6494792j/f2.image/f2.jpeg
##
##
## => In order to stop at the end, the module tries to download one more file
##    and when an HTTP error is produced, than, no more pictures are available
##
##############################################################################

# File containing the last line read
g_file_last_line_name = "__last_multiple_document_checked.cache"

# File with double resolved URL
prefix_double_resolved_file_name = "double-resolved_"

# File with undownloaded URL
prefix_unresolved_file_name = "double-unresolved_"

### Small tools

# Split the Ark ID into a list
def split_ark_id(ark_id):
    # Ark ID : /12148/bpt6k6449020t
    #match = re.match("/([a-aA-Z_0-9]*)", ark_id)
    #return (match.groups())
    # Spli the string by the '/' and remove the empty 1st
    split = re.split("/", ark_id)
    return (split[1:len(split)])

# Add a URL to the unresolved log
def update_file_unresolved_log(msg):
    ark_id_filename_input = sys.argv[1]
    unresolved_filename = prefix_unresolved_file_name + ark_id_filename_input
    MyCommonTools.update_file_ouput(msg, unresolved_filename)


# Get the web page
def get_web_page(url):
    print("## Checking URL : " + str(url))
    ## Chromium & Force size 1
    #options = Options()
    #options.add_argument("window-size=500,300")
    #driver = webdriver.Chrome(chrome_options=options)
    ## Launch Firefox
    driver = webdriver.Firefox()
    ## Force size 2
    #driver.set_window_size(500, 300)
    #size = driver.get_window_size()

    ## Open the webpage
    driver.get(url)
    ## Goto the results list : <div class="liste-resultats">
    div_liste_resultats = driver.find_element(By.CLASS_NAME, "liste-resultats")

    ## Extract all the results ID : <div class="resultat-id" id="resultat-id-X">
    ##  (where X is a number)
    div_resultats_ids = div_liste_resultats.find_elements(By.CLASS_NAME, "resultat-id")
    liste_id = []
    for element in div_resultats_ids:
        div_id = element.get_attribute("id")
        #print(str(div_id))
        liste_id.append(div_id)
    nb_results = len(liste_id)

    ## Extract all the links to the documents
    for i in range(1, nb_results):
        id_tag = "resultat-id-" + str(i)
        href_resultat = div_liste_resultats.find_element(By.CLASS_NAME, "result-contenu")

    ###### OU : pour chaque class="resultContainer", prendre le 1er href
        
    html = div_liste_resultats.get_attribute('innerHTML')
    print(html.strip())
    ## Save the full page
    #f = open("lol", "w")
    #html = driver.page_source
    #f.write(html)
    #f.close

    # resultat-id-

    ## Close one tab
    #driver.close()
    ## Close the full browser
    driver.quit()

    exit(0)

# For each line, get the web page and process each result-id
def process_lines(lines):
    url_filename_input = sys.argv[1]

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
        res = get_web_page(url)


        line_resolved = date + " " + ark_id
        MyCommonTools.update_file_ouput(line_resolved, url_resolved_filename)
        print("=> One document found")
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
