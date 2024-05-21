# BnFDebatsParlementairesDownloader-python
Downloader in python for the BnF collection "Débats Parlementaires" (Parliamentary Debates)

# Requirements:
- Python 3+
- urllib.request
- Beautiful Soup 4
- Selenium

One browser:
- Chrome
- Chromium
 sudo apt-get install chromium-chromedriver
- Firefox

# Usage:
1) __1-Choose_Range.py__ generates a file with a list of URL to test
2) __2-Get_Ark_ID.py__ tests each URL and generates :
  - a file with a list of resolved URL/Ark ID (direct access to each document containing one day of debates)
  - a file with a list of URLs which have multiple documents on the date
  - a file with a list of unresolved URLs where no documents were found
3) __3-Download_Multiple_Docs_Same_Date.py__
4) __4-Download_Date_to_JPEG.py__ downloads all of the pictures of an Ark ID of a debate (it stops when there is a 503 error/all pages where consumed) [a PDF version of the downloader is also available]

# How to Use:
- Calls the script 1 with the two dates creating a range + the prefix URL.

__python src/1-Choose_Range.py YYYY-MM-DD YYYY-MM-DD prefix_url__

- The prefix URL can be found in the "doc" folder, in columns F of the files.
It's exactly like the URL when you're on a page with the calendar, except that
you should remove the final "date.item" or "date.r=".
However, you MUST keep the final "/" in this URL.
Like this : https://gallica.bnf.fr/ark:/12148/cb328020951/
For example, if you want to download everything between the 1 July of 1893 and
the 10 July 1893 for the last prefix, just do this :

__python src/1-Choose_Range.py 1893-07-01 1893-07-10 https://gallica.bnf.fr/ark:/12148/cb328020951/__

- It produces a long list of URLs with dates (without checking if they exist or
not). Now, use the script 2 to resolve these URLs and obtain the Ark IDs.

__python src/2-Get_Ark_ID.py 1-list_url.txt__

- Four files are created, one with "resolved" URLs into Ark ID, one with
"complex" URLs where one date contains multiple documents, one with "external"
URLs where the dates redirects to external websites, and one with "unresolved"
URLs. You should check why they were not resolved. Maybe there was not any
debates this day... You can check online on Gallica if there is a document this
day or not by reading the "unresolved_" file (you can read it).
Keep in my this file is UPDATED! You should remove it if you want to check from
scratch what is available online or not.
Concerning the "complex" URLs, you must check later, with the final picture, if
it was the same document scanned multiple times (on microfilms and regular
scan) or if there really was multiple documents the same day.

__python 3-Download_Multiple_Docs_Same_Date.py 2-complex_list_url.txt__

- Two files are created, one with "resolved-bis" prefix containing the browsed
URLs with the Ark ID of each document found, and one with "unresolved-bis" URLs
for URLs which couldn't be resolved.

__python src/4-Download_Date_to_JPEG.py output_folder 2-resolved_list_url.txt__

__python src/4-Download_Date_to_JPEG.py output_folder 3-resolved-bis_complex_list_url.txt__

- Finally, use the script 4 on the "resolved_" file containing all of the ARK
IDs. An output directory name must be given (it will eventually be created).
When everything has been downloaded, it is automatically renamed (a "WIP"
folder is created, and when everything is done, it is renamed
[WIP = Work In Progress])
Inside, you'll find subdirectories with dates and ARK IDs.

# Explanations:
- The script 2 produces three outputs : "2-resolved_", "2-complex_",
"2-external_" and "2-unresolved_".
The "unresolved_" contains the URL that were not resolved... probably because
there was no debates this day!
In order to confirm, you can check online on the Gallica website: the log
contains useful informations like the day AND the day of the week (monday, ...)
The "complex_" contains the URL where each date has multiple documents. It is
more difficult to obtain the Ark ID.
The "external_" contains the URL which redirects to websites external to Gallica


- The script 4 produces a directory containing subdirectories with all of the
downloaded JPEG

- The intermediates files can be read by a human. It is simply a 2 columns file
The first column contains the date, the second column contains the data
The script 1 produces URL, the script 2 produces ARK ID, and the script 3 JPG
You can find back which date is associated with each ressource.
The two columns are separated by a space, because " " character is forbidden in
regular URL (it should be replaced by a "%20"), therefore it is safe to use it
as a splitter for data and URLs or ARK IDs.

- The JPEG downloader tries to download JPEG files until an error HTTP 503 is
produced (telling that the file does not exist/the server failed beacuse it
cannot send this ressource)
- The PDF downloader ask for the PDF containing the first 99999 pages (I hope
that no document from this time had so much pages...). As the ressource does
not have so much pages, the server sends the maximum pages it could find.
Therefore, the full PDF is sent.

# Contributors:
- PUREN Marie (Main Consumer & Projet Leader) [2023-...]
- BOISSIER Fabrice (Main Developper & Co-Projet Leader) [2023-...]
