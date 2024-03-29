import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin

URL = 'https://runeberg.org/nf/'

def fetch_volume_links(soup: BeautifulSoup):
    # Fetch the <table> element that holds the links to the volumes for each edition
    # OBS: Unfortunately it has no identifying attribute, so we just hard code it fetching the second table found in the HTML.
    edition_table = soup.find('table').find_next('table')
    rows = edition_table.find_all('tr')
    no_of_editions = len(rows[0].find_all('td'))

    editions_volume_links = []
    for row in rows:
        cols = row.find_all('td')
        volume_links = [None for _ in range(no_of_editions)]
        for i in range(len(cols)):
            # For each cell, check if there exists a link and if so, add it to edition_volume_links
            volume_link = cols[i].find('a', href=True)
            if volume_link:
                volume_links[i] = volume_link['href']
        editions_volume_links.append(volume_links)

    return editions_volume_links

def fetch_page_links(volume_link):
    volume_url = urljoin(URL, volume_link)
    response = requests.get(volume_url)
    if response.status_code != 200:
        print(f"Failed to retrieve the webpage ({volume_url}): HTTP {response.status_code}")
    else:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        def is_page_link(tag):
            if tag.name == 'a' and tag.has_attr('href'):
                has_page_link = bool(re.search(r'\d\d\d\d.html', tag['href']))  # check if it links to a page
                includes_page_numbers = bool(re.search(r'\d+-\d+', tag.text))   # check that it links to relevant encyclopedia content (i.e. no preface etc...)
                return has_page_link and includes_page_numbers
            return False
        
        # 1. Fetch all page links, which has the format 'XXXX.html' where X is a digit.
        #    Each volume html contains a lot of duplicate links, therefore we use set comprehension:
        page_links = {tag['href'] for tag in soup.find_all(is_page_link)}
        return page_links



def main():
    response = requests.get(URL)
    # Check if the request was successful
    if response.status_code != 200:
        print(f"Failed to retrieve the webpage ({URL}): HTTP {response.status_code}")
    else:
        # Parse the HTML content of 'https://runeberg.org/nf/'
        soup = BeautifulSoup(response.text, 'html.parser')
        # 1. Each edition contains a number of volumes, each with it's own hyperlink:
        edition_vol_links = fetch_volume_links(soup)

        # 2. Fetch the pages of all volumes for first and fourth edition and collect in dict:
        first_edition = {}
        fourth_edition = {}
        for vol_links in edition_vol_links:
            first_ed_vol_link = vol_links[0]
            fourth_ed_vol_link = vol_links[2]
            if first_ed_vol_link:
                first_edition[first_ed_vol_link] = fetch_page_links(first_ed_vol_link)
            if fourth_ed_vol_link:
                fourth_edition[fourth_ed_vol_link] = fetch_page_links(fourth_ed_vol_link)
        # 3. 
        

if __name__ == "__main__":
    main()