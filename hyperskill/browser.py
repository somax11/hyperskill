import sys
import os
from collections import deque
import requests
from bs4 import BeautifulSoup
import re
from colorama import Fore


class Parser:

    def __init__(self,
                 parse_tags=['title', 'p', 'a', 'h1', 'h2', 'h3', 'h3', 'h4', 'h5', 'h6', 'h7', 'ul', 'ol', 'li']):
        self.parse_tags = parse_tags

    def parse_html_to_tags(self, content):
        soup = BeautifulSoup(content, 'html.parser')
        output = soup.find_all(self.parse_tags)
        text = ""
        last_line = ""
        for i in output:
            line = i.string
            if line and line != last_line:
                last_line = line
                if i.name == "a":
                    text += Fore.BLUE + line.strip() + Fore.RESET
                else:
                    text += line.strip()
                text += "\n"
        return text


class Browser:

    def __init__(self, caches_dir):
        self.visited_sites = deque()
        self.caches_dir = caches_dir
        self.create_caches_dir()
        self.parser = Parser()
        self.command = ""

    def valid_domain(self, string):
        return bool(re.match(r'^\A([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,}\Z', string))

    def create_caches_dir(self):
        if not os.path.exists(self.caches_dir):
            os.mkdir(self.caches_dir)

    def get_cache_file_path(self, file_name):
        return self.caches_dir + '/' + file_name

    def get_url_contents(self, url):
        request_url = ""
        if 'https://' not in url:
            request_url = f'https://{url}'
        try:
            r = requests.get(request_url)
            r.raise_for_status()
            return r.text
        except requests.exceptions.HTTPError:
            return ""

    def cache_read(self, file_name):
        cache_file_path = self.get_cache_file_path(file_name)
        with open(cache_file_path) as cache:
            self.visited_sites.append(file_name)
            return cache.read()

    def cache_save(self, cache_file_path, content):
        with open(cache_file_path, 'w') as cache:
            cache.write(content)

    def go_back(self):
        popped_file_name = self.visited_sites.popleft()
        if popped_file_name in os.listdir(path=self.caches_dir):
            content = self.cache_read(popped_file_name)
            self.visited_sites.append(popped_file_name)
            print(content)

    def cached_site(self):
        file_name = self.command + '.txt'
        if file_name in os.listdir(path=self.caches_dir):
            cached_content = self.cache_read(file_name)
            self.visited_sites.append(file_name)
            print(cached_content)
        else:
            print('Error: Incorrect URL')

    def open_and_save_cache(self):
        url = self.command
        file_name = '.'.join(self.command.split('.')[:-1]) + '.txt'
        cache_file_path = self.get_cache_file_path(file_name)
        content = self.get_url_contents(url)
        if len(content) == 0:
            print('Error: Incorrect URL')
            return False
        parsed_content = self.parser.parse_html_to_tags(content)
        self.cache_save(cache_file_path, parsed_content)
        self.visited_sites.append(file_name)
        print(parsed_content)

    def browse(self):
        while True:
            self.command = input('')
            if self.command == 'exit':
                break
            elif self.command == 'back':
                self.go_back()
            elif not self.valid_domain(self.command):
                self.cached_site()
            else:
                self.open_and_save_cache()


def main():
    cache_dir = sys.argv[1]
    browser = Browser(cache_dir)
    browser.browse()


if __name__ == "__main__":
    # execute only if run as a script
    main()
