# Argv
import sys

# Regexp
import re

# Date
import datetime

# Prefix common to all parliamentary debates
g_prefix_debates = "https://gallica.bnf.fr/ark:/12148/cb328020951/"

# Example for debates of 5 february 1889
#eg_url_targeted = "https://gallica.bnf.fr/ark:/12148/cb328020951/date18890205"

##########################################################################
## The objective of this module is to generate all the URLs for debates ##
##########################################################################
##
## For example, to generate URL of debates between the 5 and 7 february 1889 :
# python 1-debats_choose_range.py 1889-02-05 1889-02-07
## ...it generates a file containing these :
# "https://gallica.bnf.fr/ark:/12148/cb328020951/date18890205"
# "https://gallica.bnf.fr/ark:/12148/cb328020951/date18890206"
# "https://gallica.bnf.fr/ark:/12148/cb328020951/date18890207"
##
##########################################################################

# Check arguments format
def check_date_format(date_str):
    # Expected Input : "1893-07-22"  --  "YYYY-mm-dd"
    match = re.fullmatch("^[0-9]{4}-[0-9]{2}-[0-9]{2}$", date_str)
    return (match != None)

# Transform my format of date into a datetime object
def transforms_date_to_datetime(input_date):
    # Input : "1893-07-22"  --  "YYYY-mm-dd"
    date_time_obj = datetime.datetime.strptime(input_date, '%Y-%m-%d')
    return (date_time_obj)

# Transform a datetime object into a triplet
def transforms_datetime_to_triplet(input_datetime):
    year = input_datetime.strftime("%Y")
    month = input_datetime.strftime("%m")
    day = input_datetime.strftime("%d")

    # Output : ("dd", "mm", "YYYY")
    date_triplet = [ day, month, year ]
    return (date_triplet)

# Generate a list of dates (day by day) in datetime object
def generate_list_of_dates(first_date, last_date):
    date_begin = transforms_date_to_datetime(first_date)
    date_end = transforms_date_to_datetime(last_date)

    delta = date_end - date_begin

    list_of_dates = [ date_begin + datetime.timedelta(days=x)
                      for x in range(delta.days + 1)]

    return (list_of_dates)

# Create a list of URL from the list of dates
def transform_list_of_dates_into_url(list_of_dates, url_prefix, url_suffix):
    list_of_url = []
    for date in list_of_dates:
        triplet = transforms_datetime_to_triplet(date)
        # String format : YYYYmmdd
        str_triplet = str(triplet[2]) + str(triplet[1]) + str(triplet[0])
        # URL building
        url = url_prefix + str_triplet + url_suffix
        list_of_url.append(url)

    return (list_of_url)

# Generate a list of URL from two dates in my format and the URL prefix + suffix
def generate_list_of_URL(first_date, last_date, url_prefix, url_suffix):
    # Input : "1893-07-22"  --  "YYYY-mm-dd"
    list_of_dates = generate_list_of_dates(first_date, last_date)
    list_of_url = transform_list_of_dates_into_url(list_of_dates,
                                                   url_prefix,
                                                   url_suffix)
    return (list_of_url)

# Write out a list into a file
def write_list_to_file(input_list, filename):
    # Clear file first
    fd = open(filename, 'w')
    fd.truncate(0)
    fd.close()
    # Then write out the list
    with open(filename, 'w') as fp:
        fp.write('\n'.join(input_list))
    fp.close()

# Check for arguments in the CLI
def main():
    # Check for missing arguments
    if (len(sys.argv) != 3):
        print("Missing parameters")
        print("")
        print("Usage: " + sys.argv[0] + " first_date last_date")
        print("")
        print("Dates format: YYYY-mm-dd  (e.g.: 1893-07-22)")
        return (-1)
    else:
        # Check for incorrect date format in one of the argument
        if ((not (check_date_format(sys.argv[1]))) or
            (not (check_date_format(sys.argv[2])))):
            print("Incorrect date format")
            print("")
            print("Usage: " + sys.argv[0] + " first_date last_date")
            print("")
            print("Dates format: YYYY-mm-dd  (e.g.: 1893-07-22)")
            return (-2)

        # If everything is good, let's process data !
        first_date = sys.argv[1]
        last_date = sys.argv[2]
        prefix_url = g_prefix_debates + "date"
        suffix_url = ""

        # Reverse dates if in incorrect order
        if (transforms_date_to_datetime(first_date) >
            transforms_date_to_datetime(last_date)):
            tmp = first_date
            first_date = last_date
            last_date = tmp

        url_list = generate_list_of_URL(first_date, last_date,
                                        prefix_url, suffix_url)
        filename = "list_url_" + first_date + "_"  + last_date + ".txt"
        write_list_to_file(url_list, filename)
        return (0)

main()

# MAIN OF TEST
def main_test():
    first_date = "1889-11-12"
    last_date = "1893-07-22"
    #last_date = "1893-10-14"

    url_targeted = "https://gallica.bnf.fr/ark:/12148/cb328020951/date18890205"
    prefix_debates = "https://gallica.bnf.fr/ark:/12148/cb328020951/"
    prefix_date = "date"
    suffix_date = ""

    list_of_dates = generate_list_of_dates(first_date, last_date)

    #print(list_of_dates)

    list_of_url = generate_list_of_URL(first_date,
                                       last_date,
                                       prefix_debates + "date",
                                       "")

    #print(list_of_url)

    filename = "list_url_" + first_date + "_"  + last_date
    write_list_to_file(list_of_url, filename)
