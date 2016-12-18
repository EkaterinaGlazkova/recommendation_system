#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from urllib.request import urlopen
from urllib.parse import quote
import argparse
import sys
import re
import os

import log
import common


def get_arguments():
    parser = argparse.ArgumentParser(
        prog = 'download',
        description = 'Download articles'
    )
    parser.add_argument(
        '--input',
        help = 'name of input file',
        dest = 'input_file'
    )
    parser.add_argument(
        'urls',
        nargs = '*',
        action = 'store',
        help = 'list of urls'
    )
    parser.add_argument(
        '--log',
        default = 'error',
        help = 'log level',
        choices = ['error', 'critical',  'debug'],
        dest = 'log_level'
    )
    return parser.parse_args()


def main():
    args = get_arguments()
    log.config(log.level(args.log_level))

    if not args.urls:
        with open(args.input_file, 'r') as f:
            args.urls = f.read().split()
    saved_htmls = set(os.listdir('DATA/HTML'))

    for link in args.urls:
        *_, name_of_article = link.strip('/').split('/')
        log.debug('Trying to save html from \'%s\'', link)
        html_file_name = name_of_article + common.HTML_SUFFIX
        if html_file_name in saved_htmls:
            log.debug('Article from \'%s\' was saved before', link)
        else:
            page = common.load_page(link)
            with open(common.HTML_ROOT + html_file_name, 'w') as file:
                file.write(page)
            log.debug('Article from \'%s\' is saved', link)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        log.critical('Force stop')
    except Exception:
        _,  value, traceback = sys.exc_info()
        log.critical(value)
        log.critical(common.tb_str(traceback))
