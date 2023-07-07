# Files
import os
import shutil
import tempfile

# HTTP & URL
import urllib.request

#############################################################################
## The objective of this module is to download all of the JPG of an Ark ID ##
#############################################################################
##
## For example, from this Ark ID :
# ark_id = "/12148/bpt6k6494792j"
## ...build these URL...
# url_short = "https://gallica.bnf.fr/ark:/12148/bpt6k6494792j"
# url_full = "https://gallica.bnf.fr/ark:/12148/bpt6k6494792j/f1.image/f1.jpeg?download=1"
## ...and finally downloading the 4 JPG.
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

def prepare_out_directory(directory):
    isExist = os.path.exists(directory)
    if not isExist:
        os.makedirs(directory)

# Download each JPG until an error occurs (when the end of document is reached)
### identifier = ark_id
### prefix_filename = output file prefix
def get_document_debat_parlementaire(identifier, directory, prefix_filename):
    print("#### Downloading document " + str(identifier) +
          " to " + str(directory) + "/" + str(prefix_filename))
    print("")

    prepare_out_directory(directory)

    page_exist = True
    page = 1
    while (page_exist):
        jpgfile = prefix_filename + "_" + str(page) + ".jpeg"
        url = 'http://gallica.bnf.fr/ark:' + identifier + '/f' + str(page) + '.image/f' + str(page) +'.jpeg?download=1'

        # Try to download a page
        print("## Downloading page " + str(page))

        ## Obsolete method
        #try:
        #    filename, headers = urllib.request.urlretrieve(url, jpgfile)
        #    print("## headers of page " + str(page))
        #    print("#########################")
        #    print(headers)
        #    print("#########################")
        #    os.rename(jpgfile, directory + jpgfile)
        #    page += 1
        #
        # If an error occured, it might be because there are no more pages
        #except Exception as e:
        #    print("Error (" + str(type(e)) + ") on " + str(identifier))
        #    page_exist = False
        #    raise

        # Prepare request
        req = urllib.request.Request(url)
        print("trying request...")
        try:
            # Send request
            response = urllib.request.urlopen(req)

        # Exception HTTP Error
        except urllib.error.HTTPError as e:
            ## Error 503 : we reached the end of the document
            if (page == 1):
                print("### HTTP ERROR ON PAGE 1:")
            else:
                print("### HTTP ERROR:")

            if hasattr(e, 'reason'):
                print('Failed to reach a server.')
                print('Reason: ', e.reason)
            if hasattr(e, 'code'):
                print('The server couldn\'t fulfill the request.')
                print('Error code: ', e.code)
                ## Error 503 : we reached the end of the document
                if ((int(e.code) == 503) and (page != 1)):
                    print("# Stopped at page " + str(page))
                    return (None)
            print("#############")
            print(e.read())
            print("#############")

            page_exist = False
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

            page_exist = False
            return (None)

        # Everything is fine
        else:
            print("OK")

            data = response.read()
            info = response.info()
            url_new = response.url
            headers = response.headers
            #text = data.decode(info.get_param('charset', 'utf-8'))
            #text = data.decode('utf-8')

            print("## url_new : " + str(url_new))
            print("## headers : " + str(headers))
            out_file = open(directory + "/" + jpgfile, 'wb')
            out_file.truncate(0)
            out_file.write(data)
            out_file.close()

            page += 1


# MAIN OF TEST
def main_debats_download_date():
    url_id1 = "/12148/cb328020951/date18891112"
    url_id2 = "/12148/bpt6k6494792j/"

    get_document_debat_parlementaire(url_id2, "./outdir/", "essai")
