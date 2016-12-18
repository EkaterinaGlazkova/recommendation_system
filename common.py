import io
import sys
import traceback
import re
import log
from urllib.request import urlopen

NAME_REGULAR_PATTERN = re.compile('((\w+-)+\w+)+')
HTML_SUFFIX = '.html'
HTML_ROOT = 'DATA/HTML/'
TXT_SUFFIX = '.txt'
TXT_ROOT = 'DATA/TXT/'
COMMON_DATE_FORMAT = '%d/%m/%Y'
LINK_DATE_FORMAT = '%Y/%m/%d'
DATE_PATTERN = re.compile('\d{4}/\d{2}/\d{2}')
HOME_PAGE_PREFFIX = "http://www.engadget.com/topics/science/page/"
LINK_PATTERN = re.compile('http://www\.engadget\.com/\d{4}/\d{2}/\d{2}/.+?/')

def tb_str(tb):
    out = io.StringIO()
    traceback.print_tb(tb, file=out)
    return out.getvalue()

def load_page(url):
    log.debug('Trying to open \'%s\'', url)
    try:
        result = urlopen(url)
    except:
        log.error('Can not open \'%s\'', url)
        raise
    else:
        if result.getcode() == 200:
            return result.read().decode('utf-8')
