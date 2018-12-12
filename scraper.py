#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Simple Web Scraper looking for URL's, email, and phone numbers.

Program accepts a website page and scrapes the page looking for URL's,
emails, and phone numbers. prints them to the std.out.

Author: Aaron Jackson
Github: TimeApollo
"""

__author__ = 'Aaron Jackson'

import argparse
import requests
import re
from HTMLParser import HTMLParser
from bs4 import BeautifulSoup


def print_urls(urls):
    """Prints list of html strings on individual lines."""
    print('\nURLs')
    print('\n'.join(set(urls)))


def print_emails(emails):
    """Prints list of emails as strings on individual lines."""
    print('\nEmails')
    print('\n'.join(set(emails)))


def print_phone_numbers(numbers):
    """Prints list of phone numbers as strings on individual lines."""
    print('\nPhone Numbers')
    print('\n'.join(set(numbers)))


def print_relative_urls(rel_urls):
    """Prints A and IMG tags' href and src urls from beautiful soup parser."""
    print('\nIMG and A tag URLS')
    print('\n'.join(set(rel_urls)))


def url_regex(content):
    """Searches string for urls."""
    urls = re.findall((
      r'http[s]?://(?:[a-zA-Z]'
      r'|[0-9]|[$-_@.&+]|[!*\(\),]'
      r'|(?:%[0-9a-fA-F][0-9a-fA-F]))+'),
      content)
    return urls


def email_regex(content):
    """Searches string for emails."""
    emails = re.findall(
        r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)', content)
    return emails


def phone_number_regex(content):
    """Searches string for phone numbers."""
    numbers = re.findall((
        r'1?\W*([2-9][0-8][0-9])'
        r'\W*([2-9][0-9]{2})\W*([0-9]{4})(\se?x?t?(\d*))?'), content)
    return numbers


def img_a_url_regex(content):
    """Searches string for . or @."""
    urls = re.findall(r'\S+[.|@]\S+', content)
    return urls


def find_urls(html_parser):
    """Returns list of urls by using the html parser."""
    data_urls = url_regex(' '.join(html_parser.text))
    return data_urls + html_parser.start_tag_attrs


def find_emails(html_parser):
    """Returns list of emails by using the html parser."""
    return email_regex(' '.join(html_parser.text))


def find_phone_numbers(html_parser):
    """Returns list of phone numbers by using the html parser."""
    number_list = []
    phone_tuples_list = phone_number_regex(' '.join(html_parser.text))
    for num in phone_tuples_list:
        number_list.append(''.join(map(str, num)))
    return number_list


def find_relative_urls(bs):
    """Returns list of Relative URLS from A and IMG tags."""
    a_tags = []
    for link in bs.find_all('a'):
        if link.get('href'):
            a_tags.append(link.get('href'))
        if link.get('src'):
            a_tags.append(link.get('src'))
    img_tags = []
    for link in bs.find_all('img'):
        if link.get('href'):
            img_tags.append(link.get('href'))
        if link.get('src'):
            img_tags.append(link.get('src'))
    urls = img_a_url_regex(' '.join(a_tags + img_tags))
    return urls


def scraper_html_parser():
    """Creates an HTML parser class."""
    class ScraperHTMLParser(HTMLParser):
        """Html parser class with functions overridden."""
        def __init__(self):
            """Reinitialize the html parser methods and make new attributes."""
            HTMLParser.__init__(self)
            self.text = []
            self.start_tag_attrs = []

        def handle_starttag(self, tag, attrs):
            """Appends value if tag is img or svg and has src location."""
            if tag == 'svg' or tag == 'img':
                for name, value in attrs:
                    if name == 'src' \
                      or name == 'data-src' \
                      or name == 'data-image':
                        self.start_tag_attrs.append(value)

        def handle_data(self, data):
            """Strips empty space from content and returns in list."""
            data = data.strip()
            if data:
                self.text.append(data)

    return ScraperHTMLParser()


def scraper(url):
    """Does GET request at URL and returns content of server response."""
    r = requests.get(url)
    # print(r.encoding)print(r.json())print(r.text)
    return r.content


def parser():
    """Creates and returns an argparse cmd line option parser."""
    parser = argparse.ArgumentParser(
        description="Webscraping provided website")
    parser.add_argument("url", help="URL to be webscraped")

    return parser


def main():
    """Webscraping implementation."""
    arg_parser = parser().parse_args()
    url = arg_parser.url

    # gets content of website entered
    web_content = scraper(url)

    # instantiates a html_parser and then runs it
    html_parser = scraper_html_parser()
    html_parser.feed(str(web_content))

    """ These lines are the new code using Beautiful Soup """
    # instantiates beautiful soup with web_content
    bs = BeautifulSoup(web_content)
    rel_urls = find_relative_urls(bs)

    """ End of new code. """

    # finds info from html parser
    urls = find_urls(html_parser)
    emails = find_emails(html_parser)
    numbers = find_phone_numbers(html_parser)

    # prints info from find functions
    print_urls(urls)
    print_emails(emails)
    print_phone_numbers(numbers)

    # print for beautiful soup urls
    print_relative_urls(rel_urls)


if __name__ == "__main__":
    main()
