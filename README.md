# BnFDebatsParlementairesDownloader-python
Downloader in python for the BnF collection "Débats Parlementaires" (Parliamentary Debates)

# Requirements:
- Python 3+
- Beautiful Soup

# Usage:
1) __1-debats_choose_range.py__ generates a file with a list of URL to test
2) __2-debats_get_ark_id.py__ tests each URL and generates a file with a list of resolved URL/Ark ID (direct access to each document containing one day of debates)
3) __3-debats_download_date.py__ downloads all of the pictures of an Ark ID of a debate (it stops when there is a 503 error/all pages where consumed) [a PDF version of the downloader is also available]

# How to Use:
- Calls the script 1 with the two dates creating a range + the prefix URL.
The prefix URL can be found in the "doc" folder, in columns F of the files.
It's exactly like the URL when you're on a page with the calendar, except that
you should remove the final "date.item" or "date.r=".
However, you MUST keep the final "/" in this URL.
Like this : https://gallica.bnf.fr/ark:/12148/cb328020951/date18891121
For example, if you want to download everything between the 1 July of 1893 and
the 10 July 1893 for the last prefix, just do this :

__python src/1-debats_choose_range.py 1893-07-01 1893-07-10 https://gallica.bnf.fr/ark:/12148/cb328020951/date18891121__

- It produces a long list of URLs with dates (without checking if they exist or
not). Now, use the script 2 to resolve these URLs and obtain the Ark IDs.

__python src/2-debats_get_ark_id.py list_url.txt__

- Two files are created, one with "resolved" URLs into Ark ID, and one with
"unresolved" URLs. You should check why they were not resolved. Maybe there
was not any debates this day... You can check online on Gallica if there is a
document this day or not by reading the "unresolved_" file (you can read it).
Keep in my this file is UPDATED! You should remove it if you want to check from
scratch what is available online or not.

- Next, use the script 3 on the "resolved_" file containing all of the ARK IDs:

__python src/3-debats_download_date.py resolved_list_url.txt__

- An output directory will be created. When everything has been downloaded, it
should automatically be renamed "output_JPG_..." instead of "output_WIP_JPG".
(WIP = Work In Progress)
Inside, you'll find subdirectories with dates and ARK IDs.

# Explanations:
- The script 2 produces two outputs : "resolved_" and "unresolved_".
The "unresolved_" contains the URL that were not resolved... probably because
there was no debates this day!
In order to confirm, you can check online on the Gallica website: the log
contains useful informations like the day AND the day of the week (monday, ...)

- The script 3 produces a directory containing subdirectories with all of the
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
