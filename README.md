# BnFDebatsParlementairesDownloader-python
Downloader in python for the BnF collection "Débats Parlementaires" (Parliamentary Debates)

# Requirements:
- Python 3+
- Beautiful Soup

# Usage:
1) __1-debats_choose_range.py__ generates a file with a list of URL to test
2) __2-debats_get_ark_id.py__ tests each URL and generates a file with a list of resolved URL/Ark ID (direct access to each document containing one day of debates)
3) __3-debats_download_date.py__ downloads all of the pictures of an Ark ID of a debate (it stopsz when there is a 503 error/all pages where consumed)

# Contributors:
- PUREN Marie (Main Consumer & Projet Leader) [2023-...]
- BOISSIER Fabrice (Main Developper & Co-Projet Leader) [2023-...]
