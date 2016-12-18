import re
import sys
import argparse
import os
import random

import log
import common


def get_arguments():
    parser = argparse.ArgumentParser(
        prog = 'mark',
        description = 'Gives articles for reading and marking.'
        )
    parser.add_argument(
        '--output',
        help = 'Name of output file.',
        dest = 'output_file',
        default = 'DATA/valued_articles.txt'
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
    cleaned_articles = list()
    for article in list(os.listdir(common.TXT_ROOT)):
        if re.match('.*\.txt', article):
            cleaned_articles.append(article)

    if not os.path.exists(args.output_file):
        with open(args.output_file, 'tw', encoding='utf-8'):
            pass
    with open(args.output_file, 'r') as file:
        valued_articles = set(file.read().split())

    current_number_of_articles = len(valued_articles)
    with open(args.output_file, 'a') as file:
        while True:
            article = cleaned_articles[random.randint(0, len(cleaned_articles) - 1)]
            if article not in valued_articles:
                log.debug('article name: %s', article)
                valued_articles.add(article)
                with open(common.TXT_ROOT + article) as txt_file:
                    for line in txt_file:
                        print(line)
                value = 2
                print('Value the article (only 1 or 0 are acceptable)')
                while value != '0' and value != '1':
                    value = input()
                file.write(article + ' ' + value + '\n')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        log.critical('Force stop')
    except Exception:
        _,  value, traceback = sys.exc_info()
        log.critical(value)
        log.critical(common.tb_str(traceback))
