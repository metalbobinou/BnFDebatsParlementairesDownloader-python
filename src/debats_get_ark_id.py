# Regexp
import re

# HTTP & URL
import urllib.request

# Files
#import shutil
#import tempfile

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
    match = re.search('^https?://gallica\.bnf\.fr/ark:', no_item_url)
    # if no prefix found, let's send back the URL
    if (match == None):
        return (None)

    # if prefix is found, let's keep only the ark id following it
    ark_id = no_item_url[match.end(0):]
    return (ark_id)

# Resolve a URL and extract its Ark ID
def get_ark_id_from_date_URL(url_date, url_original):
    # Let's resolve date URL and obtain the new URL
    url_resolved = get_ressource_url(url_date)
    # if resolved URL is empty, let's write it
    if (url_resolved == None):
        print("## Error :")
        print("  no ressource found")
        print("url_original : --" + url_original + "--")

        return (None)

    # if the date has been resolved;, let's parse it for Ark ID
    ## first, let's remove the suffix if it exists : the final ".item"
    url_no_suffix = remove_suffix_item_from_url(url_resolved)
    ## next, let's remove the prefix : the http[s]://...
    ark_id = remove_prefix_https_from_url(url_no_suffix)
    if (ark_id == None):
        print("## Error :")
        print("  can't find the Ark ID in the URL")
        print("url_original : --" + url_original + "--")
        print("url_resolved : --" + url_resolved + "--")
        print("url_no_suffix : --" + url_no_suffix + "--")

        return (None)

    # Ark ID has been found
    return (ark_id)


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
