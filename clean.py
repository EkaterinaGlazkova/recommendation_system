#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from html.parser import HTMLParser
from urllib.request import quote, urlopen
import re
import io
import argparse
import sys
import collections
import os

import log
import common


def get_arguments():
    parser = argparse.ArgumentParser(
        prog = 'clean',
        description = 'Get text from html'
    )
    parser.add_argument(
        'urls',
        nargs = '*',
        action = 'store',
        help = 'list of urls'
    )
    parser.add_argument(
        '--input',
        help = 'name of input file',
        dest = 'input_file'
    )
    parser.add_argument(
        '--log',
        default = 'error',
        help = 'log level',
        choices = ['error', 'critical',  'debug'],
        dest = 'log_level'
    )
    return parser.parse_args()


class Parser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self._title_text = ''
        self._second_title_text = ''
        self._article_text = io.StringIO()
        self._in_header_tag = False
        self._in_h1_tag = False
        self._in_h2_tag = False
        self._in_div_tag = False
        self._in_p_tag = False
        self._saved_text_in_div = False

    def handle_starttag(self, tag, attrs):
        if tag == 'header':
            attrs = dict(attrs)
            if attrs.get('class') == "o-feed_listing@m- o-feed_bleed@m- mb-10@m mb-40@tp+":
                self._in_header_tag = True
        if self._in_header_tag and tag == 'h1':
            self._in_h1_tag = True
        if self._in_header_tag and tag == 'h2':
            self._in_h2_tag = True
        if tag == 'div':
            attrs = dict(attrs)
            if attrs.get('class') == "article-text c-gray-1" or \
                    attrs.get('class') == "article-text c-gray-1 no-review":
                self._in_div_tag = True
                self._saved_text_in_div = False
        if tag == 'p' and self._in_div_tag:
            self._in_p_tag = True

    def handle_endtag(self, tag):
        if self._in_header_tag and tag == 'header':
            self._in_header_tag = False
        if self._in_h1_tag and tag == 'h1':
            self._in_h1_tag = False
        if self._in_h2_tag and tag == 'h2':
            self._in_h2_tag = False
        if self._in_div_tag and tag == 'div' and self._saved_text_in_div:
            self._in_div_tag = False
        if self._in_p_tag and tag == 'p':
            self._in_p_tag = False
            self._article_text.write('\n')

    def handle_data(self, data):
        if self._in_h1_tag:
            self._title_text += data.strip()
        if self._in_h2_tag:
            self._second_title_text += data.strip()
        if self._in_p_tag:
            self._saved_text_in_div = True
            self._article_text.write(data)

    def parse(self, page):
        self.feed(page)
        article_text = collections.namedtuple("Article", ['title', 'subtitle', 'text'])
        return (article_text(
            title = self._title_text,
            subtitle = self._second_title_text,
            text =  self._article_text.getvalue())
        )


def parse(page):
    return Parser().parse(page)


def main():
    args = get_arguments()
    log.config(log.level(args.log_level))
    if not args.urls:
        with open(args.input_file, 'r') as f:
            args.urls = f.read().split()
    saved_htmls = set(os.listdir('DATA/HTML'))
    cleaned_htmls = set(os.listdir('DATA/TXT'))

    for link in args.urls:
        *_, name_of_article = link.strip('/').split('/')
        log.debug('Trying to clean html from \'%s\'', link)
        html_file_name = name_of_article + common.HTML_SUFFIX
        txt_file_name = name_of_article + common.TXT_SUFFIX
        if html_file_name not in saved_htmls:
            log.error('Article from \'%s\' was not saved before in html', link)
            continue
        if txt_file_name in cleaned_htmls:
            log.debug('Article from \'%s\' was cleaned before', link)
            continue
        with open(common.HTML_ROOT + html_file_name) as html_file:
            page = html_file.read()
        parsed_data = parse(page)
        with open(common.TXT_ROOT + txt_file_name, 'w') as txt_file:
            txt_file.write("\n".join(parsed_data))
        log.debug('Article from \'%s\' is cleaned and saved in \'%s\'', link, txt_file_name)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        log.critical('Force stop')
    except Exception:
        _,  value, traceback = sys.exc_info()
        log.critical(value)
        log.critical(common.tb_str(traceback))
