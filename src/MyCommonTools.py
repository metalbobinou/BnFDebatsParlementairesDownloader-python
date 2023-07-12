# OS & Files
import os

# Date
import datetime

#####################################
### Small tools useful everywhere ###
#####################################

### Date tools

# Generate a string with the date and time
def get_date_and_time():
    now = datetime.datetime.now()
    str_time = now.strftime("%Y-%m-%d_%Hh%Mm%Ss")
    return (str_time)
# Generate a string with the date
def get_date():
    now = datetime.datetime.now()
    str_time = now.strftime("%Y-%m-%d")
    return (str_time)
# Generate a string with the time
def get_time():
    now = datetime.datetime.now()
    str_time = now.strftime("%Hh%Mm%Ss")
    return (str_time)

# Get the day of the week from a date in str (YYYY-MM-DD)
def get_day_or_the_week(date):
    datetime_object = datetime.datetime.strptime(date, "%Y-%m-%d")
    # weekday() : Monday = 0 ... Sunday = 6
    int_DOTW = datetime_object.weekday()
    # isoweekday() : Monday = 1 ... Sunday = 7
    iso_DOTW = datetime_object.isoweekday()
    # named day of the week
    DOTW = datetime_object.strftime('%A')
    return (DOTW)


### File tools

# Update the file recording last line processed
def update_file_last_line(cur_line, file_last_line_name):
    fd = open(file_last_line_name, 'w')
    fd.truncate(0)
    fd.write(str(cur_line))
    fd.close()

# Add a line in a file
def update_file_ouput(line, filename_output):
    fd = open(filename_output, 'a')
    fd.write(str(line) + "\n")
    fd.close()

# Create a directory if it does not exist
def prepare_out_directory(directory):
    isExist = os.path.exists(directory)
    if not isExist:
        os.makedirs(directory)
