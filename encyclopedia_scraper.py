import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
import os
import pathlib

URL = 'https://runeberg.org/nf/'

def fetch_edition_volume_links(soup: BeautifulSoup):
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

def fetch_volume_page_links(volume_link):
    volume_url = urljoin(URL, volume_link)
    response = requests.get(volume_url)
    if response.status_code != 200:
        print(f"Failed to retrieve the webpage ({volume_url}): HTTP {response.status_code}")
    else:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        def is_page_link(tag):
            if tag.name == 'a' and tag.has_attr('href'):
                has_page_link = bool(re.search(r'\d\d\d\d.html',   tag['href']))  # check if it links to a page
                includes_page_numbers = bool(re.search(r'\d+-\d+', tag.text))     # check that it links to relevant encyclopedia content (i.e. no preface etc...)
                return has_page_link and includes_page_numbers
            return False
        
        # 1. Fetch all page links, which has the format 'XXXX.html' where X is a digit.
        #    Each volume html contains a lot of duplicate links, therefore we use set comprehension:
        page_links = {tag['href'] for tag in soup.find_all(is_page_link)}
        return page_links

def fetch_volume_page_content(volume_link, page_link):
    volume_url = urljoin(URL, volume_link)
    page_url = urljoin(volume_url, page_link)
    response = requests.get(page_url)
    if response.status_code != 200:
        print(f"Failed to retrieve the webpage ({page_url}): HTTP {response.status_code}")
    else:
        soup = BeautifulSoup(response.text, 'html.parser')
        # 1. Define regex strings
        #    Check for keywords listed at top of the document
        entries_re = r"On this page \/ på denna sida\n(.*?)<<\sprev.*page\s>>"
        #    Check for proofread statement
        start_re = r"(?:This page has been proofread at least once.+\(historik\)|This page has never been proofread\. / Denna sida har aldrig korrekturlästs\.)"
        #    Page content
        content_re = r"(?:\d+\n\n.*?\n\n\d+)?(.*?)"
        #    End tag
        end_re = r"<<\sprev.*page\s>>"
        regex = entries_re + r".*" + start_re + content_re + end_re
        match = re.search(regex, soup.find('p').text, re.DOTALL)
        # 2. Extract entries and content
        entries_text = match.group(1).strip(' \n')
        content_text = match.group(2).strip(' \n')
        return entries_text, content_text

def download_edition(edition_dir_path, edition_vols: dict):
    for vol_link, page_links in edition_vols.items():
        vol_dir = f"{edition_dir_path}\\{vol_link.strip('/')}"
        # Create volume directory:
        pathlib.Path(vol_dir).mkdir(exist_ok=False)
        for page_link in page_links:
            filename = page_link.strip('.html') + ".txt"
            # Fetch the text content of each page and save locally to text files within each volume:
            # TODO
            # text = fetch_volume_page_content(vol_link, page_link)
            # with open(f"{vol_dir}\\{filename}", mode='x') as f:
            #     f.write(text)

def main():
    base_dir = os.path.dirname(os.path.realpath(__file__))
    first_edition_path = f"{base_dir}\\nf_first_edition"
    fourth_edition_path = f"{base_dir}\\nf_fourth_edition"
    try:
        pathlib.Path(first_edition_path).mkdir(exist_ok=False)
        pathlib.Path(fourth_edition_path).mkdir(exist_ok=False)
    except FileExistsError:
        print("Directories already exist: the encyclopedia has already been fetched?")

    response = requests.get(URL)
    # Check if the request was successful
    if response.status_code != 200:
        print(f"Failed to retrieve the webpage ({URL}): HTTP {response.status_code}")
    else:
        # Parse the HTML content of 'https://runeberg.org/nf/'
        soup = BeautifulSoup(response.text, 'html.parser')
        # 1. Each edition contains a number of volumes, each with it's own hyperlink:
        edition_vol_links = fetch_edition_volume_links(soup)

        # 2. Fetch the pages of all volumes for first and fourth edition and collect in dicts:
        first_edition_vols = {}
        fourth_edition_vols = {}
        for vol_links in edition_vol_links:
            first_ed_vol_link = vol_links[0]
            fourth_ed_vol_link = vol_links[2]
            if first_ed_vol_link:
                first_edition_vols[first_ed_vol_link] = fetch_volume_page_links(first_ed_vol_link)
            if fourth_ed_vol_link:
                fourth_edition_vols[fourth_ed_vol_link] = fetch_volume_page_links(fourth_ed_vol_link)

        # 3. Create local folder structure for saving encyclopedia locally
        #    Create volume directories:
        download_edition(first_edition_path, first_edition_vols)
        download_edition(fourth_edition_path, fourth_edition_vols)
        

if __name__ == "__main__":
    main()