#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from urllib.request import quote, urlopen
import argparse
import datetime
import re
import sys
import os

import log
import common


def parse_date(data_str):
    return datetime.datetime.strptime(data_str, common.COMMON_DATE_FORMAT)


def get_arguments():
    parser = argparse.ArgumentParser(
        prog = 'update',
        description = 'Find and save links.'
    )
    parser.add_argument(
        '--from',
        help = 'set the first date in format "dd/mm/year" (default: 01/01/1970).',
        dest = 'begin',
        type = parse_date,
        default = '01/01/1970'
    )
    parser.add_argument(
        '--to',
        help = 'set the last date in format "dd/mm/year" (default: today).',
        type = parse_date,
        dest = 'end',
        default = datetime.datetime.today()
    )
    parser.add_argument(
        '--output',
        help = 'save all the found links to',
        dest = 'output_file',
        default = sys.stdout,
        type = argparse.FileType('w')
    )
    parser.add_argument(
        '--log',
        default = 'error',
        help = 'log level',
        choices = ['error', 'critical',  'debug'],
        dest = 'log_level'
    )
    return parser.parse_args()


def extract_links(page_text):
    return common.LINK_PATTERN.findall(page_text)


def get_date_from_link(link):
    return datetime.datetime.strptime(common.DATE_PATTERN.search(link).group(0), "%Y/%m/%d")


def in_interval(date, args):
    return args.end >= date >= args.begin


def check_previous(number, end):
    if number == 1:
        return True
    page_text = common.load_page(common.HOME_PAGE_PREFFIX + quote(str(number - 1)))
    links = extract_links(page_text)
    last_date_from_page = get_date_from_link(links[-1])
    if last_date_from_page > end:
        return True
    return False


def bin_search(min_num, max_num, begin, end):
    if min_num == max_num:
        return min_num
    middle = (min_num + max_num) // 2
    page_text = common.load_page(common.HOME_PAGE_PREFFIX + quote(str(middle)))
    links = extract_links(page_text)
    if not links:
        return bin_search(min_num, middle, begin, end)
    else:
        links = extract_links(page_text)
        first_date_from_page = get_date_from_link(links[0])
        last_date_from_page = get_date_from_link(links[-1])
        check_previous(middle, end)
        if last_date_from_page <= end and check_previous(middle, end):
            return middle
        if last_date_from_page < end:
            return bin_search(min_num, middle, begin, end)
        if first_date_from_page > end:
            return bin_search(middle + 1, max_num, begin, end)


def get_start_page(begin, end):
    min_num = 1
    max_num = 1
    while True:
        page_text = common.load_page(common.HOME_PAGE_PREFFIX + quote(str(max_num)))
        links = extract_links(page_text)
        if links:
            last_date_from_link = get_date_from_link(links[-1])
            if last_date_from_link < end:
                return bin_search(min_num, max_num, begin, end)
        else:
            return bin_search(min_num, max_num, begin, end)
        min_num = max_num
        max_num *= 2


def main():
    args = get_arguments()
    log.config(log.level(args.log_level))
    num_page = get_start_page(args.begin, args.end)
    log.debug("Number of the first page is %s", num_page)
    some_link_was_found = True
    new_links = set()
    saved_links = set(os.listdir('DATA/HTML'))

    while some_link_was_found:
        log.debug("Searches the links on the page number %s", num_page)
        page_text = common.load_page(common.HOME_PAGE_PREFFIX + quote(str(num_page)))
        links = extract_links(page_text)
        some_link_was_found = False
        for link in links:
            *_, name_of_article = link.strip('/').split('/')
            if link not in new_links and (name_of_article + common.HTML_SUFFIX) not in saved_links:
                date_from_link = get_date_from_link(link)
                if in_interval(date_from_link, args):
                    some_link_was_found = True
                    new_links.add(link)
        num_page += 1

    if not new_links:
        log.error("No articles in set period")

    args.output_file.write('\n'.join(new_links))
    log.debug("All the links have been found")
    if args.output_file is not sys.stdout:
        log.debug("All the links have been saved in %s", str(args.output_file.name))

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        log.critical('Force stop')
    except Exception:
        _,  value, traceback = sys.exc_info()
        log.critical(value)
        log.critical(common.tb_str(traceback)) 
