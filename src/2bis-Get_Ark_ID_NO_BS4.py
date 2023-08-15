# Argv & OS
import sys
import os

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
import http.client

### Contains small tools for dates and others
import MyCommonTools

##############################################################################
## The objective of this module is to resolve a date URL and get the Ark ID ##
##############################################################################
##
## For example, resolving this :
# url = "https://gallica.bnf.fr/ark:/12148/cb328020951/date18891112"
## ...into this...
# url_resolved = "https://gallica.bnf.fr/ark:/12148/bpt6k6494792j.item"
## ...finally getting this :
# ark_id = "/12148/bpt6k6494792j"
##
##############################################################################

# File containing the last line read
g_file_last_line_name = "__2bis-last_url_resolved.cache"

# File with resolved URL / Date has one document
prefix_resolved_file_name = "2bis-resolved_"

# File with external URL / Date has one URL out of Gallica
prefix_external_file_name = "2bis-external_"

# File with unresolved URL
prefix_unresolved_file_name = "2bis-unresolved_"

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

# Add a URL to the unresolved log
def update_file_unresolved_log(msg):
    url_filename_input = os.path.basename(sys.argv[1])
    unresolved_filename = prefix_unresolved_file_name + url_filename_input
    MyCommonTools.update_file_ouput(msg, unresolved_filename)

# Remove the ".item" suffix if it exists
def remove_suffix_item_from_url(url):
    match = re.search('\.item$', url)
    # if no ".item" found, let's send back the URL
    if (match == None):
        return (url)

    # if ".item" found, let's remove it
    #print(str(match.group(0))
    #print(str(match.start(0)))
    #print(str(match.end(0)))
    no_item_url = url[:match.start(0)]
    #print(str(no_item_url))
    return (no_item_url)

# Remove the http[s]://gallica.bnf.fr/ark: prefix in a URL
def remove_prefix_https_from_url(url):
    match = re.search('^https?://gallica\.bnf\.fr/ark:', url)
    # if no prefix found, let's send back the URL
    if (match == None):
        return (None)

    # if prefix is found, let's keep only the ark id following it
    ark_id = url[match.end(0):]
    return (ark_id)


### Main URL resolver

# Send a GET request with a date URL, and obtain the resolved one as answer
def get_ressource_url(url):
    print("## Getting new URL for : " + str(url))

    # Prepare request
    req = urllib.request.Request(url)
    print("trying request...")
    try:
        # Send request + Limit by time
        response = urllib.request.urlopen(req, timeout=600)

    # Exception HTTP Error
    except urllib.error.HTTPError as e:
        print("### HTTP ERROR:")
        if hasattr(e, 'reason'):
            print('Failed to reach a server.')
            print('Reason: ', e.reason)
        if hasattr(e, 'code'):
            print('The server couldn\'t fulfill the request.')
            print('Error code: ', e.code)
        print("#############")
        print(e.read())
        print("#############")
        return (None)

    # Exception URL Error
    except urllib.error.URLError as e:
        print("### URL ERROR:")
        if hasattr(e, 'reason'):
            print('We failed to reach a server.')
            print('Reason: ', e.reason)
        if hasattr(e, 'errno'):
            print('The server couldn\'t fulfill the request.')
            print('Error code (errno): ', e.errno)
        print("#############")
        if hasattr(e, 'read'):
            print(e.read())
        else:
            print("(no e.read())")
        print("#############")
        return (None)

    # Timeout reached
    except TimeoutError as e:
        print("### TIMEOUT ERROR:")
        print("# Connection has been hanged... (probably because of no answer from server)")
        print("# Stopped at page " + str(page))
        print(str(e))
        print("#############")
        return (None)

    # Catch "Ctrl + C" closer
    except KeyboardInterrupt as e:
        print("### KEYBOARD INTERRUPT (Ctrl+C ?):")
        print("# Stopped at page " + str(page))
        print(str(e))
        print("#############")
        logging.error(traceback.format_exc())
        return (None)

    # All other exceptions (like "http.client.RemoteDisconnected")
    except Exception as e:
        print("### UNKNOWN ERROR:")
        print(str(e))
        print("#############")
        return (None)

    # Everything is fine
    else:
        print("OK")

        # Read the HTTP response
        try:
            data = response.read()
            url_new = response.url
            headers = response.headers
            status = response.status
            #text = data.decode(info.get_param('charset', 'utf-8'))
        except http.client.IncompleteRead as e:
            print("--- ERROR : INCOMPLETE HTTP RESPONSE ---")
            print(str(e))
            print("#############")
            logging.error(traceback.format_exc())
            return (None)

        print("## url_new : " + str(url_new))
        print("## headers : " + str(headers))
        print("## status  : " + str(status))
        #with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        #    shutil.copyfileobj(response, tmp_file)
        #shutil.copy(tmp_file.name, "html.txt")

        return (url_new)


# Resolve a URL and extract its Ark ID
def get_ark_id_from_date_URL(url_date):
    # Let's resolve date URL and obtain the new URL
    url_resolved = get_ressource_url(url_date)
    external_gallica = False

    # if resolved URL is empty, let's write it
    if (url_resolved is None):
        print("## Error :")
        print("  no ressource found")
        print("url_date : --" + url_date + "--")
        return (None, external_gallica)

    # if URL hasn't changed, let's return it and write an error...
    if (url_resolved == url_date):
        print("## Warning :")
        print("  URL hasn't changed. Let's skip it...")
        print("url_date : --" + url_date + "--")
        return (url_date, external_gallica)

    # if URL is out of Gallica, let's put it in a specific file
    if (not (MyCommonTools.check_gallica_url(url_resolved))):
        external_gallica = True
        print("## Warning :")
        print("  URL is out of Gallica")
        print("    url_date : --" + url_date + "--")
        print("    liste_resultats : --" + str(liste_resultats) + "--")
        return (url_resolved, external_gallica)

    # if the date has been resolved;, let's parse it for Ark ID
    ## first, let's remove the suffix if it exists : the final ".item"
    url_no_suffix = remove_suffix_item_from_url(url_resolved)
    ## next, let's remove the prefix : the http[s]://...
    ark_id = remove_prefix_https_from_url(url_no_suffix)
    if (ark_id is None):
        print("## Error :")
        print("  can't find the Ark ID in the URL")
        print("url_date : --" + url_date + "--")
        print("url_resolved : --" + url_resolved + "--")
        print("url_no_suffix : --" + url_no_suffix + "--")

        return (None, external_gallica)

    # Ark ID has been found
    return (ark_id, external_gallica)

# For each line, try to resolve it, or write in unresolved logs that it failed
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
        update_file_unresolved_log("# Launching URL resolver/Ark ID solver at " +
                                   now.strftime("%d/%m/%Y %H:%M:%S"))
    except IOError:
        print("+++ IOError AT BEGINNING while writing in Unresolved log +++")
        return (-3)

    # Continue the process of the file from the last state
    url_resolved_filename = prefix_resolved_file_name + url_filename_input
    url_external_filename = prefix_external_file_name + url_filename_input
    while (cur_line != max_line):
        #url = lines[cur_line]
        ### Manages file with 2 columns
        line = lines[cur_line]
        line_split = re.split(" ", line)
        date = line_split[0]
        url = line_split[1]
        ###
        #ark_id = get_ark_id_from_date_URL(url)
        answers = get_ark_id_from_date_URL(url)
        ark_id = answers[0]
        external_gallica = answers[1]

        # if ark_id was not found, write down the number where it failed and stop
        if (ark_id is None):
            #print("ERROR: Failed at line " + str(cur_line))
            #print("DATE : " + date)
            #print("URL : " + url)
            #MyCommonTools.update_file_last_line(cur_line,
            #                                    g_file_last_line_name)
            MyCommonTools.error_save_last_line(cur_line, date, url,
                                               g_file_last_line_name)
            return (-3)

        # if URL hasn't changed, let's skip it (add write it in the unresolved log)
        if (ark_id == url):
            #update_file_unresolved_log(url)
            ### Add day and name of the day in the log
            print("=> Ark ID didn't changed (no documents, or multiples)")
            try:
                DOTW = MyCommonTools.get_day_or_the_week(date)
                line_unresolved = date + " " + DOTW + " " + url
                update_file_unresolved_log(line_unresolved)
            except IOError:
                 print("+++ IOError while writing in Unresolved log +++")
                 MyCommonTools.error_save_last_line(cur_line, date, url,
                                                    g_file_last_line_name)
                 return (-3)
            ###
            print("#############################################################")
            cur_line += 1
            g_cur_line = cur_line
            continue

        # if resolved link is external of gallica, let's write it in specific file
        if (external_gallica == True):
            print("=> External URL")
            try:
                line_external = date + " " + url
                MyCommonTools.update_file_ouput(line_external,
                                                url_external_filename)
            except IOError:
                print("+++ IOError while writing in External log +++")
                MyCommonTools.error_save_last_line(cur_line, date, url,
                                                   g_file_last_line_name)
                return (-3)
            ###
            print("#############################################################")
            cur_line += 1
            g_cur_line = cur_line
            continue


        # if everything OK, let's write the result in the output file
        #update_file_ouput(ark_id, url_resolved_filename_output)
        ### Add date before Ark_ID
        # out format : "YYYY-MM-DD Ark_ID"
        print("=> One document found")
        try:
            line_resolved = date + " " + ark_id
            MyCommonTools.update_file_ouput(line_resolved,
                                            url_resolved_filename)
        except IOError:
            print("+++ IOError while writing in Resolved log +++")
            MyCommonTools.error_save_last_line(cur_line, date, url,
                                               g_file_last_line_name)
            return (-3)
        ###
        print("#############################################################")
        # read next line
        cur_line += 1
        g_cur_line = cur_line

    # If everything ended well, let's remove the cache file with last state
    if (os.path.exists(g_file_last_line_name)):
        os.remove(g_file_last_line_name)
    # And let's rename the final resolved list by adding a "_FINAL" inside
    if (os.path.exists(url_resolved_filename)):
        url_resolved_filename_final = os.path.splitext(url_resolved_filename)[0]
        url_resolved_filename_final = url_resolved_filename_final + "_final.txt"
        os.rename(url_resolved_filename, url_resolved_filename_final)
    else:
        print("--no resolved file were created during this script--")
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
