import requests
from bs4 import BeautifulSoup

youtube_url = 'https://www.youtube.com'
url = 'https://www.youtube.com/results?search_query='

keyword = input('請輸入要找的音樂關鍵字')
response = requests.get(url + keyword)
html_doc = response.text
soup = BeautifulSoup(html_doc, "lxml")

# print(soup.prettify()) # 把排版後的 html 印出來

div_result = soup.find('div', id='content')

a_result = div_result.find_all('a')

for a in a_result:
    print(youtube_url + a['href'], a.text)