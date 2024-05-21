# Files
import sys
import os
from io import StringIO, BytesIO

# Exceptions tracking
import traceback
import logging

# Signal handler
import signal

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

# Selenium Chrome & Chromium
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# Selelnium Firefox
#from selenium.webdriver.firefox.options import Options
#from selenium.webdriver.firefox.service import Service

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
g_file_last_line_name = "__3-last_multiple_document_checked.cache"

# File with resolved-bis URL
prefix_resolved_bis_file_name = "3-resolved-mul_"

# File with external URL
prefix_external_bis_file_name = "3-external-mul_"

# File with undownloaded URL
prefix_unresolved_file_name = "3-unresolved-mul_"

# Global "Current Line" (for signal processing)
g_cur_line = 0

### Signal handler

# Main handler : save current line and exit
def signal_graceful_exit():
    print("ERROR: Stopped at line " + str(g_cur_line))
    MyCommonTools.update_file_last_line(g_cur_line,
                                        g_file_last_line_name)
    sys.exit(-5)

# SIGTERM handler
def signal_term_handler(signal, frame):
    print("!!!!! SIGTERM CAUGHT !!!!!")
    signal_graceful_exit()

# Default handler
def signal_default_handler(sig_num, frame):
    signal_num = str(sig_num)
    signal_name = str(signal.Signals(sig_num).name)
    print("!!!!! SIGNAL (" + signal_num + " " + signal_name + ") CAUGHT !!!!!")
    signal_graceful_exit()

# Declare which signals to handle
def signal_declare_handlers():
    ## SIGTERM = regular "kill"
    signal.signal(signal.SIGTERM, signal_term_handler)
    ## SIGINT = Ctrl+C
    signal.signal(signal.SIGINT, signal_default_handler)
    ## SIGABRT = abrot(3)
    signal.signal(signal.SIGABRT, signal_default_handler)
    ## SIGQUIT = quit from keyboard
    signal.signal(signal.SIGQUIT, signal_default_handler)


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
        ## Cerome
        #### Force size 1
        #options1 = Options()
        #options1.add_argument("window-size=500,300")
        #driver = webdriver.Chrome(chrome_options=options1)
        #### No GUI
        #options = webdriver.ChromeOptions()
        #options.add_argument("--headless=new")
        #driver = webdriver.Chrome(options=options)
        #print("-- Chrome arguments prepared --")

        ## Chromium
        #### Method 1
        options = Options()
        options.BinaryLocation = "/usr/bin/chromium-browser"
        driver = webdriver.Chrome(executable_path="/usr/bin/chromedriver",options=options)
        #### Method 2
        #options = webdriver.ChromeOptions()
        #options.headless = True
        ##options.BinaryLocation = "/usr/bin/chromium-browser"
        ##options.add_argument("--headless=new")
        #options.add_argument("--headless")
        #options.add_argument("--no-sandbox");
        #options.add_argument("--disable-dev-shm-usage");
        #driver = webdriver.Chrome(options=options)
        ##driver = webdriver.Chrome(executable_path="/usr/bin/chromedriver",options=options)
        print("-- Chromium arguments prepared --")

        ## Firefox & No GUI
        ##### Selenium 3
        #options = Options()
        #options.add_argument("--headless")
        #driver = webdriver.Firefox(options=options)
        ##### Selenium 4+
        ##driver_path = f"{settings.BASE_DIR}/geckodriver"
        #driver_path="/snap/firefox/4209/usr/lib/firefox/geckodriver"
        #options = webdriver.FirefoxOptions()
        ##options.binary_location = "/usr/lib/firefox"
        #options.binary_location = "/snap/bin/firefox"
        #options.add_argument("--headless")
        ##driver = webdriver.Firefox(options=options)
        #driver = webdriver.Firefox(service=Service(executable_path=driver_path), options=options)
        #####
        ## Force size 2
        #driver.set_window_size(500, 300)
        #size = driver.get_window_size()
        #print("-- Firefox arguments prepared --")

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

    # Catch "Ctrl + C" closer
    except KeyboardInterrupt as e:
        print("### KEYBOARD INTERRUPT (Ctrl+C ?):")
        print(str(e))
        print("#############")
        logging.error(traceback.format_exc())
        return (None)

    # All other exceptions
    except Exception as e:
        print("### UNKNOWN ERROR WHEN REACHING URL:")
        print(str(e))
        print("#############")
        driver.quit()
        return (None)

    ## Save the full page
    #f = open("file.htm", "w")
    #html = driver.page_source
    #f.write(html)
    #f.close

    ## Goto the results list : <div class="liste-resultats">
    ## (if it is not found, retry to fetch the page)
    for i in range (0, 5):
        try:
            div_liste_resultats = driver.find_element(By.CLASS_NAME, "liste-resultats")
        except NoSuchElementException as e:
            print("##### Couldn't find 'liste-result' in HTML...")
            print("    [try " + str(i) + " retrying " + str(5 - i) + " times again")
            try:
                driver.get(url)
            except (NoSuchElementException, WebDriverException) as e:
                print("##### WEBDRIVER ERROR WHEN REACHING URL:")
                print(str(e))
                print("#############")
                driver.quit()
                return (None)
            except KeyboardInterrupt as e:
                print("### KEYBOARD INTERRUPT (Ctrl+C ?):")
                print(str(e))
                print("#############")
                logging.error(traceback.format_exc())
                return (None)
            except Exception as e:
                print("##### UNKNOWN ERROR WHEN REACHING URL:")
                print(str(e))
                print("#############")
                driver.quit()
                return (None)
        else:
            # If "liste-resultats" was found, let's continue
            break
        if (i == 4):
            print("### Couldn't find any 'liste-resultats' in HTML")
            print("### Ending on error here.")
            ## Save the full page
            f = open("file_no_liste_resultats.htm", "w")
            html = driver.page_source
            f.write(html)
            f.close
            return (None)

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
    global g_cur_line
    url_filename_input = os.path.basename(sys.argv[1])

    # File has been read and is in memory, everything is fine
    cur_line = 0
    g_cur_line = 0
    max_line = len(lines)
    ## Open the temporary file for last processed line
    if (os.path.isfile(g_file_last_line_name)):
        fd = open(g_file_last_line_name, "r")
        file_last_line = fd.read()
        fd.close()
        cur_line = int(file_last_line)
        g_cur_line = cur_line

    # Be aware of signals from now [When context has been put back]
    signal_declare_handlers()
    ## Update the unresolved log for saying an instance has been launched
    now = datetime.datetime.now()
    try:
        update_file_unresolved_log("# Launching URL multiple docs getter at " +
                                   now.strftime("%d/%m/%Y %H:%M:%S"))
    except IOErrror:
        print("+++ IOError AT BEGINNING while writing in Unresolved log +++")
        return (-3)

    # Continue the process of the file from the last state
    url_resolved_filename = prefix_resolved_bis_file_name + url_filename_input
    url_external_filename = prefix_external_bis_file_name + url_filename_input
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
            #print("ERROR: Failed at line " + str(cur_line))
            #print("DATE : " + date)
            #print("URL : " + url)
            #MyCommonTools.update_file_last_line(cur_line,
            #                                    g_file_last_line_name)
            MyCommonTools.error_save_last_line(cur_line, date, url,
                                               g_file_last_line_name)
            return (-3)

        ## Write down the URLs
        i = 1
        for new_url in URLs:
            ## If URL is external of Gallica, let's write it in specific file
            if (not (MyCommonTools.check_gallica_url(new_url))):
                print("=> External URL")
                try:
                    line_external = date + "-" + str(i) + " " + new_url
                    MyCommonTools.update_file_ouput(line_external,
                                                    url_external_filename)
                except IOError:
                    print("+++ IOError while writing in External log +++")
                    MyCommonTools.error_save_last_line(cur_line, date, url,
                                                       g_file_last_line_name)
                    return (-3)
            else:
                ## else, let's put it in the regular file
                print("=> Document found")
                try:
                    ark_id = extract_ark_id_from_url(new_url)
                    line_resolved = date + "-" + str(i) + " " + ark_id
                    MyCommonTools.update_file_ouput(line_resolved, url_resolved_filename)
                except IOError:
                    print("+++ IOError while writing in Resolved log +++")
                    MyCommonTools.error_save_last_line(cur_line, date, url,
                                                       g_file_last_line_name)
                    return (-3)

            i += 1
        ###
        print("#############################################################")
        # read next line
        cur_line += 1
        g_cur_line = cur_line

    # If everything ended well, let's remove the cache file with last state
    if (os.path.exists(g_file_last_line_name)):
        os.remove(g_file_last_line_name)
    # And let's rename the final double resolved list by adding a "_FINAL" inside
    if (os.path.exists(url_resolved_filename)):
        url_resolved_filename_final = os.path.splitext(url_resolved_filename)[0]
        url_resolved_filename_final = url_resolved_filename_final + "_final.txt"
        os.rename(url_resolved_filename, url_resolved_filename_final)
    else:
        print("--no resolved-bis file were created during this script--")
    # And let's rename the final external list by adding a "_FINAL" inside
    if (os.path.exists(url_external_filename)):
        url_external_filename_final = os.path.splitext(url_external_filename)[0]
        url_external_filename_final = url_external_filename_final + "_final.txt"
        os.rename(url_external_filename, url_external_filename_final)
    else:
        print("--no external cases file were created during this script--")
    print("<<< LIST PROCESSING CORRECTLY FINISHED ! >>>")

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
        sys.exit(-1)
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
            sys.exit(-2)

	# In other case, when evrything is fine, let's process lines
        MyCommonTools.print_time("%%%% BEGIN PROCESSING")
        ret = process_lines(lines)
        MyCommonTools.print_time("%%%% END PROCESSING")

        sys.exit(ret)

main()
