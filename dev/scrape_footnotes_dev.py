import requests
from bs4 import BeautifulSoup

url = 'https://cdn-dev.economistdatateam.com/jobs/pds/code-test/index.html'

response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")
table = soup.find("table")
ul = soup.find_all("ul")

tmp = soup.find('ul', id='notes')
tmp_li = tmp.find_all("li")

# convert tmp_li to dict
footnotes_dict = {}
for li in tmp_li:
    footnotes_dict[li['data-mark']] = li.text.replace('\n', ' ').strip()

