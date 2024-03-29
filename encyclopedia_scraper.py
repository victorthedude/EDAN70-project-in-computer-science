import requests
from bs4 import BeautifulSoup

URL = 'https://runeberg.org/nf/'


def fetch_volume_links(soup: BeautifulSoup):
    # Fetch the <table> element that holds the links to the volumes for each edition
    # Unfortunately it has no identifying attribute, so we just rely on it being the second table found in the HTML.
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

# def fetch_page_links(volume_link):
#     response = requests.get(URL + volume_link)
#     page_links = []
#     if response.status_code != 200:
#         print(f"Failed to retrieve the webpage: HTTP {response.status_code}")
#     else:
#         soup = BeautifulSoup(response.text, 'html.parser')
#         links = soup.find_all('a', href=True)
#         for link in links:
#             if link['href'] == 

def main():
    response = requests.get(URL)
    # Check if the request was successful
    if response.status_code != 200:
        print(f"Failed to retrieve the webpage: HTTP {response.status_code}")
    else:
        # Parse the HTML content of the page with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        # 1. Fetch volume links:
        edition_vol_links = fetch_volume_links(soup)
        # 2. For each volume link: fetch page links

        # 3. 
        # Now you can find elements by their tag name, class_, id, etc.
        # For example, to find all <a> tags (hyperlinks) in the page:
        # links = soup.find_all('a')
        
        # for link in links:
        #     print(link.get('href'))  # Print the href attribute of each link

if __name__ == "__main__":
    main()