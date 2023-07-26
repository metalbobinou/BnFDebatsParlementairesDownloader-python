# Files
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

### Contains small tools for dates and others
import MyCommonTools

######################################################################
## The objective of this module is to download the PDF of an Ark ID ##
######################################################################
##
## For example, from this Ark ID :
# ark_id = "/12148/bpt6k6494792j"
## ...build this URL...
# url_short = "https://gallica.bnf.fr/ark:/12148/bpt6k6494792j"
# url_full = "https://gallica.bnf.fr/ark:/12148/bpt6k6494792j/f1.image/f1n4.pdf?download=1"
##
## !!! WARNING !!!
##
## After the fnal "f", the "n" is followed by the number of pages you want.
## If you put a number bigger than the maxmimum, everything is downloaded.
## ...let's put 99999 !
##
##############################################################################

# File containing the last line read
g_file_last_line_name = "__4P-last_ark_id_pdf_downloaded.cache"

# File with unresolved URL
prefix_undownloaded_file_name = "4P-undownloaded_"

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

# Split the Ark ID into a list
def split_ark_id(ark_id):
    # Ark ID : /12148/bpt6k6449020t
    #match = re.match("/([a-aA-Z_0-9]*)", ark_id)
    #return (match.groups())
    # Spli the string by the '/' and remove the empty 1st
    split = re.split("/", ark_id)
    return (split[1:len(split)])

# Add a URL to the undownloaded log
def update_file_undownloaded_log(msg):
    ark_id_filename_input = os.path.basename(sys.argv[2])
    undownloaded_filename = prefix_undownloaded_file_name + ark_id_filename_input
    MyCommonTools.update_file_ouput(msg, undownloaded_filename)


### Main PDF downloader

# Download PDF by asking for the 99999 first pages
### identifier = ark_id
### directory = directory where to put files
### prefix_filename = output file prefix
def get_document_PDF_debat_parlementaire(ark_id, directory_output, filename_prefix):
    print("#### Processing document " + str(ark_id) +
          " to " + str(directory_output) + "/" + str(filename_prefix))
    print("")

    MyCommonTools.prepare_out_directory(directory_output)

    # Try to download a page
    print("## Downloading Ark ID [PDF] (" + ark_id + ")")

    # Filename of the PDF after download
    pdffile = filename_prefix + ".pdf"

    # URL of the PDF to reach for this Ark ID
    # https://gallica.bnf.fr/ark:/12148/bpt6k6494792j/f1.image/f1n4.pdf?download=1
    #url = 'http://gallica.bnf.fr/ark:' + ark_id + '/f1.image/f1n' + '99999' + '.pdf?download=1'
    url_gallica_prefix = 'http://gallica.bnf.fr/ark:'
    url_ark_id = ark_id
    url_page = '/f1.image/f1n' + str(99999) + '.pdf?download=1'
    url = url_gallica_prefix + url_ark_id + url_page

    # Prepare request
    req = urllib.request.Request(url)
    print("trying request...")
    try:
        # Send request + Limit by time
        response = urllib.request.urlopen(req, timeout=600)

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
        if hasattr(e, 'read'):
            print(e.read())
        else:
            print("(no e.read())")
        print("#############")

        page_exist = False
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

        # Get HTTP response
        data = response.read()
        info = response.info()
        url_new = response.url
        headers = response.headers
        status = response.status
        #text = data.decode(info.get_param('charset', 'utf-8'))
        #text = data.decode('utf-8')
        print("## url_new : " + str(url_new))
        #print("## headers : " + str(headers))
        print("## status  : " + str(status))

        # Write out the current file
        try:
            out_file = open(directory_output + "/" + pdffile, 'wb')
            out_file.truncate(0)
            out_file.write(data)
            out_file.close()
        except IOError:
            print("++++ IOError : Couldn't write the PDF output file ++++")
            print("  output filename : " + str(directory_output + "/" + pdffile))
            return (None, error_503)

        print("###################################")

    # Let's return the number of pages written
    return (1)


# For each line, try to download all of the JPEG
def process_lines(lines):
    global g_cur_line
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
    ## Update the undownloaded log for saying an instance has been launched
    now = datetime.datetime.now()
    try:
        update_file_undownloaded_log("# Launching Ark ID downloader for debates at " +
                                     now.strftime("%d/%m/%Y %H:%M:%S"))
    except IOErrror:
        print("+++ IOError AT BEGINNING while writing in Undownloaded log +++")
        return (-3)

    ## Prepare output directory
    dirname_output = sys.argv[1]

    ## Continue the process of the file from the last state
    while (cur_line != max_line):
        #ark_id = lines[cur_line]
        ### Manages file with 2 columns
        line = lines[cur_line]
        line_split = re.split(" ", line)
        date = line_split[0]
        ark_id = line_split[1]
        ###

        ark_id_splitted = split_ark_id(ark_id)
        ## No need for subfolder in the PDF case
        #dirname = dirname_output + "_WIP_PDF" + "/" + date + "_" + str(ark_id_splitted[1])
        dirname = dirname_output + "_WIP_PDF" + "/"
        filename_prefix = date + "_" + str(ark_id_splitted[1])

        # Ark ID, directory output, filename prefix
        pages_written = get_document_PDF_debat_parlementaire(ark_id,
                                                             dirname,
                                                             filename_prefix)

        ## If an error occurred, let's save where we were
        if (pages_written == None):
            print("=> No document to download found")
            try:
                line_undownloaded = date + " " + ark_id
                update_file_undownloaded_log(line_undownloaded)
                ### IF YOU WISH TO STOP THE SCRIPT IN CASE OF ERROR, UNCOMMENT RETURN
                MyCommonTools.error_save_last_line(cur_line, date, ark_id,
                                                   g_file_last_line_name)
                return (-3)
            except IOError:
                print("+++ IOError while writing in Undownloaded log +++")
                MyCommonTools.error_save_last_line(cur_line, date, ark_id,
                                                   g_file_last_line_name)
                return (-3)

        ## If only one page were written... do something ? [unusable in the PDF case]
        #if (pages_written == 1):
        #    update_file_unresolved_log(url)
        #    cur_line += 1
        #    g_cur_line = cur_line
        #    continue
        ######################

        print("#############################################################")
        # read next line
        cur_line += 1
        g_cur_line = cur_line

    # If everything ended well, let's remove the cache file with last state
    if (os.path.exists(g_file_last_line_name)):
        os.remove(g_file_last_line_name)
    # And let's rename the folder by adding a "_FINAL" inside
    dirname_final = dirname_output + "_PDF" + "_" + MyCommonTools.get_date_and_time()
    os.rename(dirname_output + "_WIP_PDF",  dirname_final)

    return (0)

# Check for arguments in the CLI
def main():
    # Check for missing arguments
    if (len(sys.argv) != 3):
        print("Missing parameters")
        print("")
        print("Usage: " + sys.argv[0] + " output_folder list_of_Ark_IDs")
        print("")
        print("File list_of_Ark_IDs format: [one Ark ID per line]")
        print("[date] [Ark ID]")
        print("date : YYYY-MM-DD     Ark ID : /12148/bpt6k64490143")
        exit(-1)
    else:
        ark_id_filename_input = sys.argv[2]
        # Check if file is readable
        try:
            with open(ark_id_filename_input) as fd:
                ## Put the whole file in memory in a list
                lines = [line.rstrip() for line in fd]
                #### OR ####
                ## Read and process file line by line (one read per line)
                #for line in fd:
                #    print(line.rstrip())

        # If file is unreadable, let's manage the exception
        except IOError:
            print("File " + ark_id_file_input + " must exist and be readable")
            print("")
            print("Usage: " + sys.argv[0] + " output_folder list_of_Ark_IDs")
            print("")
            print("File list_of_Ark_IDs format: [one Ark ID per line]")
            print("[date] [Ark ID]")
            print("date : YYYY-MM-DD     Ark ID : /12148/bpt6k64490143")
            exit(-2)


        # In other case, when evrything is fine, let's process lines
        MyCommonTools.print_time("%%%% BEGIN PROCESSING")
        ret = process_lines(lines)
        MyCommonTools.print_time("%%%% END PROCESSING")

        exit(ret)

main()
