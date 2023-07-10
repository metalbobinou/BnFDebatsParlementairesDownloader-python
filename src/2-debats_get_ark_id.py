# Argv & OS
import sys
import os

# Regexp
import re

# Date
import datetime

# HTTP & URL
import urllib.request

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
g_file_last_line_name = "__last_url_resolved.cache"

# File with unresolved URL
prefix_unresolved_file_name = "unresolved_"

### Small tools

# Generate a string with the date ad time
def get_date_and_time():
    now = datetime.datetime.now()
    str_time = now.strftime("%Y-%m-%d_%Hh%Mm%Ss")
    return (str_time)

# Update the cache recording last line processed
def update_file_last_line(cur_line):
    fd = open(g_file_last_line_name, 'w')
    fd.truncate(0)
    fd.write(str(cur_line))
    fd.close()

# Add a URL to the unresolved log
def update_file_unresolved_log(msg):
    unresolved_filename = prefix_unresolved_file_name + sys.argv[1]
    fd = open(unresolved_filename, 'a')
    fd.write(str(msg) + "\n")
    fd.close()

# Add a line in a file
def update_file_ouput(url_resolved, filename_output):
    fd = open(filename_output, 'a')
    fd.write(str(url_resolved) + "\n")
    fd.close()

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
        # Send request
        response = urllib.request.urlopen(req)

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
        if hasattr(e, 'code'):
            print('The server couldn\'t fulfill the request.')
            print('Error code: ', e.code)
        print("#############")
        print(e.read())
        print("#############")
        return (None)

    # Everything is fine
    else:
        print("OK")

        data = response.read()
        url_new = response.url
        headers = response.headers
        #text = data.decode(info.get_param('charset', 'utf-8'))

        print("## url_new : " + str(url_new))
        print("## headers : " + str(headers))
        #with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        #    shutil.copyfileobj(response, tmp_file)
        #shutil.copy(tmp_file.name, "html.txt")

        return (url_new)


# Resolve a URL and extract its Ark ID
def get_ark_id_from_date_URL(url_date):
    # Let's resolve date URL and obtain the new URL
    url_resolved = get_ressource_url(url_date)
    # if resolved URL is empty, let's write it
    if (url_resolved == None):
        print("## Error :")
        print("  no ressource found")
        print("url_date : --" + url_date + "--")
        return (None)

    # if URL hasn't changed, let's return it and write an error...
    if (url_resolved == url_date):
        print("## Warning :")
        print("  URL hasn't changed. Let's skip it...")
        print("url_date : --" + url_date + "--")
        return (url_date)

    # if the date has been resolved;, let's parse it for Ark ID
    ## first, let's remove the suffix if it exists : the final ".item"
    url_no_suffix = remove_suffix_item_from_url(url_resolved)
    ## next, let's remove the prefix : the http[s]://...
    ark_id = remove_prefix_https_from_url(url_no_suffix)
    if (ark_id == None):
        print("## Error :")
        print("  can't find the Ark ID in the URL")
        print("url_date : --" + url_date + "--")
        print("url_resolved : --" + url_resolved + "--")
        print("url_no_suffix : --" + url_no_suffix + "--")

        return (None)

    # Ark ID has been found
    return (ark_id)

# For each line, try to resolve it, or write in unresolved logs that it failed
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
    update_file_unresolved_log("# Launching URL resolver for debates at " +
                                   now.strftime("%d/%m/%Y %H:%M:%S"))

    # Continue the process of the file from the last state
    url_resolved_filename_output = "resolved_" + url_filename_input
    while (cur_line != max_line):
        url = lines[cur_line]
        ark_id = get_ark_id_from_date_URL(url)
        # if ark_id was not found, write down the number where it failed and stop
        if (ark_id == None):
            update_file_last_line(cur_line)
            update_file_error_log("Failed at line " + str(cur_line))
            update_file_error_log("URL : " + url)
            return (-3)

        # if URL hasn't changed, let's skip it (add write it in the unresolved log)
        if (ark_id == url):
            update_file_unresolved_log(url)
            cur_line += 1
            continue

        # if everything OK, let's write the result in the output file
        update_file_ouput(ark_id, url_resolved_filename_output)
        print("#############################################################")
        # read next line
        cur_line += 1

    # If everything ended well, let's remove the cache file with last state
    if (os.path.exists(g_file_last_line_name)):
        os.remove(g_file_last_line_name)
    # And let's rename the final resolved list by adding a "_FINAL" inside
    url_resolved_filename_final = os.path.splitext(url_resolved_filename_output)[0]
    url_resolved_filename_final = url_resolved_filename_final + "_final.txt"
    os.rename(url_resolved_filename_output, url_resolved_filename_final)

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
        return (-1)
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
            return (-2)

        # In other case, when evrything is fine, let's process lines
        ret = process_lines(lines)

        return (ret)

main()


# MAIN OF TEST
def main_debats_get_ark_id():
    url_id1 = "/12148/cb328020951/date18891112"
    url_id2 = "/12148/bpt6k6494792j/"

    url_id1 = "https://gallica.bnf.fr/ark:/12148/cb328020951/date18891112"
    url_id2 = "https://gallica.bnf.fr/ark:/12148/bpt6k6494792j.item"

    url_id = url_id1
    new_url = get_ark_id_from_date_URL(url_id)

    print("Old URL : " + url_id1)
    print("New URL : " + new_url)
    print("Expect  : " + url_id2)
