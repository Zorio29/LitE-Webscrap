import os
import re
import urllib.request
import sys
import getopt
import ntpath

from bs4 import BeautifulSoup
from unidecode import unidecode

resPatternExclude = re.compile(u'[\u00bf-\uffff]')


def is_printable(string):
    """Return if the string parameter is printable following a RegEx validation."""
    return not bool(resPatternExclude.search(string))


def print_usage():
    """Print the correct usage of this script."""
    print("Usage: parser.py [optionals] ([-s SITE] -p PATH -o FILE | [-s SITE] -l FILE | -a UID | -m | -h)")
    print("-s SITE --site=SITE      # (optional) the website to obtain the file, by default "
          "'https://www.literotica.com/s/'")
    print("-p PATH --path=PATH      # the path within the website")
    print("-o FILE --output=FILE    # the output file")
    print("-l FILE --list=FILE      # a list file")
    print("-a UID --author=UID      # an author identifier in order to download all their works")
    print("-m --manual              # manual entry")
    print("-h --help                # print this help")
    print("-f --force               # (optional) force manual actions to default (delete, replace...)")
    print("-d --debug               # (optional) debug mode")


def run_site_mode(param_str_full_file, param_str_filename, param_str_path, param_str_website, param_bln_force_flag=False):
    """Run the scrapping for a single site and generates a file
    param_str_full_file      --> File name with format and full path where de output will be generated.
    param_str_filename       --> Name of the file to be generated. For documentation, appears on the file header.
    param_str_path           --> Name of the path within the website. For documentation, appears on the file header.
    param_str_website        --> Full website to scrap.
    param_bln_force_flag     --> Use default action when user confirmation is needed. By default False.
    """
    # If file exists it is deleted
    if os.path.exists(param_str_full_file):
        self_str_confirm = "n"
        if not param_bln_force_flag:
            self_str_confirm = input("File exists, delete? (Y/n): ")
        if (self_str_confirm.lower() == "y") or param_bln_force_flag:
            os.remove(param_str_full_file)
        else:
            print("Could not create file")
            sys.exit()

    # File configuration - Open file and set style
    self_txt_io_file = open(param_str_full_file, 'w')
    self_str_header = '<head><link rel="stylesheet" type="text/css" href="Style.css"></head><body><h2>' + param_str_filename \
                 + ' from: ' + param_str_path + '</h2>'
    self_txt_io_file.write(str(self_str_header))

    # Open de main body of the page
    self_str_web_current = param_str_website
    self_req_page = urllib.request.urlopen(self_str_web_current)
    self_soup_page = BeautifulSoup(self_req_page, features="lxml")
    self_tag_parse_header = self_soup_page.find("div", class_="b-story-header")
    self_str_write = str(self_tag_parse_header.next)
    if is_printable(self_str_write):
        self_txt_io_file.write(self_str_write)
    else:
        self_txt_io_file.write(unidecode(self_str_write))
    self_tag_parse = self_soup_page.find("div", class_="b-story-body-x x-r15")

    # Setup for following pages
    self_tag_old_parse = ""
    self_int_counter = 1

    # While the new page parse is different from the old one parse, continue printing
    while self_tag_old_parse != self_tag_parse:
        # Print page number
        self_txt_io_file.write('<h4>---Page ' + str(self_int_counter) + '---</h4>')

        # Print each of the lines within the body
        self_str_tag_name = self_tag_parse.name
        self_tag_sub_parse = self_tag_parse
        self_lst_tags = ['div']
        # Check if the tag is an wrapper in the list
        while True:
            if self_str_tag_name in self_lst_tags:
                self_tag_sub_parse = self_tag_sub_parse.next
                self_str_tag_name = self_tag_sub_parse.name
                if self_str_tag_name is None:
                    break  # If the node has no tag, no need to check the list
            else:
                break  # If not in the list, exit. The elements within the body have been reached
        # For each element, print them until no element remains
        while self_tag_sub_parse is not None:
            if self_tag_sub_parse.name == "strong":
                self_str_write = str("<h2>" + str(self_tag_sub_parse.next) + "</h2>")
            else:
                self_str_write = str(self_tag_sub_parse)
            if is_printable(self_str_write):
                self_txt_io_file.write(self_str_write)
            else:
                self_txt_io_file.write(unidecode(self_str_write))
            self_tag_sub_parse = self_tag_sub_parse.nextSibling

        # Check for following page
        self_tag_old_parse = self_tag_parse
        # file.write(str(parse))
        self_int_counter += 1
        self_str_web_current = param_str_website + "?page=" + str(self_int_counter)
        self_req_page = urllib.request.urlopen(self_str_web_current)
        self_soup_page = BeautifulSoup(self_req_page, features="lxml")
        self_tag_parse = self_soup_page.find("div", class_="b-story-body-x x-r15")

    # Close the body and the file
    self_str_footer = '</body>'
    self_txt_io_file.write(str(self_str_footer))
    self_txt_io_file.close()

    # End
    print("File " + str(param_str_full_file) + " generated")


def run_author_mode(param_int_author_uid):
    """Run the scrapping for all the files generated for an author.
    param_int_author_uid --> identifier for the author.
    """
    self_str_web_author = "https://www.literotica.com/stories/memberpage.php?uid=" + param_int_author_uid \
                          + "&page=submissions"
    self_req_page = urllib.request.urlopen(self_str_web_author)
    self_soup_page = BeautifulSoup(self_req_page, features="lxml")
    self_tag_parse_link = self_soup_page.find_all("a", class_="bb")

    for self_tag in self_tag_parse_link:
        self_tag_link = self_tag.get("href")
        self_tag_name = self_tag.next.text
        self_str_tag_filename = re.sub(r"[^\w\-_. ]", "", self_tag_name.replace(" ", "_"))
        self_str_tag_file = self_str_tag_filename + ".html"
        run_site_mode(self_str_tag_file, self_str_tag_filename, self_tag_link, self_tag_link, True)


def run_list_mode(param_str_list_file, param_str_site=""):
    """Run the scrapping for all the sites listed in the list file.
    param_str_list_file  --> file with the list of sites to scrap.
    param_str_site       --> website to add at the beginning of the paths in the file. Can be empty.
    """
    self_file_parse = open(param_str_list_file, "r")

    for self_site in self_file_parse.read().splitlines():
        self_str_site_name = re.sub(r"[^\w\-_. ]", "", self_site.replace(" ", "_"))
        self_str_site_file = self_str_site_name + ".html"
        self_str_web_site = param_str_site + self_site
        run_site_mode(self_str_site_file, self_str_site_name, self_site, self_str_web_site, True)


# Parameters - parse the input parameters
try:
    argv = sys.argv[1:]
    opts, args = getopt.getopt(argv, "s:p:o:l:a:mhfd",
                               ["site=", "path=", "output=", "list=", "author=", "manual", "help", "force", "debug"])
except getopt.GetoptError:
    print("Parameters are not valid - Invalid parameter found")
    print_usage()
    sys.exit(2)
str_site = "https://www.literotica.com/s/"
bln_force_flag = bln_author_mode = bln_list_mode = bln_site_mode = False
str_list_file = str_path = str_filename = str_full_file = int_author_uid = str_website = None
for opt, arg in opts:
    if opt in ("-h", "--help"):
        print_usage()
        sys.exit()
    elif opt in ("-d", "--debug"):
        print('Number of arguments:', len(sys.argv), 'arguments.')
        print('Argument List:', str(sys.argv))
    elif opt in ("-m", "--manual"):
        str_mode = input("Please enter the mode - Website parse, Author parse or Parse from list (P/a/l): ")
        if str_mode.lower() == "a":
            print("Option entered: Author parse")
            int_author_uid = input("Please enter the UID of the author: ")
            bln_author_mode = True
        elif str_mode.lower() == "l":
            print("Option entered: List parse")
            str_site_aux = input("Please enter the site to parse (Enter to use by default): ")
            if str_site_aux != "":
                str_site = str_site_aux
            str_list_file = input("Please enter the filename of the list file to parse: ")
            bln_list_mode = True
        elif str_mode.lower() in ("p", ""):
            print("Option entered: Website parse")
            str_site_aux = input("Please enter the site to parse (Enter to use by default): ")
            if str_site_aux != "":
                str_site = str_site_aux
            str_path = input("Please enter the path to parse: ")
            str_website = str_site + str_path
            print("You entered " + str(str_website))
            str_filename = input("Please enter the filename to generate: ")
            str_full_file = str_filename + ".html"
            print("You entered " + str(str_full_file))
        else:
            print("Option entered not valid")
            sys.exit(2)
        break
    elif opt in ("-f", "--force"):
        bln_force_flag = True
    elif opt in ("-s", "--site"):
        str_site = arg
    elif opt in ("-p", "--path"):
        str_path = arg
        bln_site_mode = True
    elif opt in ("-o", "--output"):
        str_filename = arg
        str_full_file = str_filename + ".html"
        str_filename = ntpath.basename(str_filename)
    elif opt in ("-a", "--author"):
        int_author_uid = arg
        bln_author_mode = True
    elif opt in ("-l", "--list"):
        str_list_file = arg
        bln_list_mode = True

# Check validity of parsed parameters and complete missing info
if (not bln_site_mode or bln_list_mode or bln_author_mode) and (
        bln_site_mode or not bln_list_mode or bln_author_mode) and (
        bln_site_mode or bln_list_mode or not bln_author_mode):  # not(blnSiteMode xor blnListMode xor blnAuthorMode)
    print("Parameters are not valid - Multiple modes selected")
    sys.exit(2)
if (str_list_file is None) and (str_path is None or str_full_file is None) and (int_author_uid is None):
    print("Parameters are not valid - Minimum required data not found")
    sys.exit(2)
if str_website is None and str_path is not None:
    str_website = str_site + str_path

# Run the specific module
if bln_site_mode:
    run_site_mode(str_full_file, str_filename, str_path, str_website, bln_force_flag)
elif bln_author_mode:
    run_author_mode(int_author_uid)
elif bln_list_mode:
    run_list_mode(str_list_file, str_site)
