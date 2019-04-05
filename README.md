# LitE-Webscrap
A small python script to scrap text websites into a one-page html file. Right now tested only with the web html format for Literotica.

## Dependencies
* **Python 3+**
* **Beautiful Soup**: easily obtain the html tags in the body of the webpage, drop all the rest. [Installing Beautiful Soup documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#installing-beautiful-soup)
* **lxml**: an specific parser for BeautifulSoup. [Installing a Parser for BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#installing-a-parser)
* **Unidecode**: some pages have characters that are hard to encode, it is easier to transform them into something readable. [Unidecode on PyPI](https://pypi.org/project/Unidecode/)

## Usage
1. From the console call `python parser.py -h`
2. The following will be printed:
    ```
    Usage: parser.py [optionals] ([-s SITE] -p PATH -o FILE | [-s SITE] -l FILE | -a UID | -m | -h)
    -s SITE --site=SITE      # (optional) the website to obtain the file, by default 'https://www.literotica.com/s/'
    -p PATH --path=PATH      # the path within the website
    -o FILE --output=FILE    # the output file
    -l FILE --list=FILE      # a list file
    -a UID --author=UID      # an author identifier in order to download all their works
    -m --manual              # manual entry
    -h --help                # print this help
    -f --force               # (optional) force manual actions to default (delete, replace...)
    -d --debug               # (optional) debug mode
    ```
 
### manual execution
1. From the console call `python parser.py -m`
2. Enter the required parameters. (See example for more info)
3. A html file is generated. 
* The header generates the following: "[Filename] from: [site-url]" followed by the header of the page itself.
* Every page change is introduced with --Page [Number]-- in order to easily see if something went wrong.
  
## Example
Let's say we want to obtain the html from https://www.literotica.com/s/three-square-meals-ch-01
### manual execution
* From the console call `python parser.py -m`
* `Please enter the mode - Website parse, Author parse or Parse from list (P/a/l):` [press Enter key]
* `Option entered: Website parse`
* `Please enter the site to parse (Enter to use by default):` [press Enter key]
* `Please enter the path to parse:` three-square-meals-ch-01
* `You entered https://www.literotica.com/s/three-square-meals-ch-01`
* `Please enter the filename to generate:` TSM01
* `You entered TSM01.html`
* `File TSM01.html generated`

### parametrized execution
#### single site mode
* From the console call `python parser.py -p three-square-meals-ch-01 - o TSM01`
* `File TSM01.html generated`

#### author mode
* In the author page find the UID in the url. 
    * For example, author `oneshotofsinglemalt` has the following url https://www.literotica.com/stories/memberpage.php?uid=3454890&page=submissions.
    * The UID for the author would be `3454890`.
* From the console call `python parser.py -a 3454890`.
* For each of this author stories a file will be created.
    * The file name will be the title removing special characters and replacing spaces with underscores.
    * A story named `Story title: Bk.01 Ch.01` would generate `Story_title_Bk.01_Ch.01.html`
* `File <NAME> generated` will be printed for each of the files the script generates.
* This process can take a long time. It took me about 15-20 minutes to obtain all chapters of Three Square Meals, for example.

#### list mode
* Create a text file with each of the urls in one line.
    * For example `site_list.txt`:

    ```
    the-marilona
    the-girl-from-the-bar
    ```
* From the console call `python parser.py -l site_list.txt`
* `File <NAME> generated` will be printed for each of the files the script generates.

### results
And in all cases would generate a files with the header: 
```
<FILE_NAME> from: <FILE_URL>
<TITLE>
```
For example for three-square-meals-ch-01 would be:
```
TSM01 from: three-square-meals-ch-01
Three Square Meals Ch. 001
```
