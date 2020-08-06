import requests
from bs4 import BeautifulSoup

youtube_url = 'https://www.youtube.com'

keyword = input('請輸入要找的歌曲關鍵字: ')
resp = requests.get('https://www.youtube.com/results?search_query=' + keyword)

soup = BeautifulSoup(resp.text, 'lxml')

# print(soup.prettify())
# print(soup.title)
# print(soup.title.name)
# print(soup.title.string)

# print(soup.a)
# print(soup.a['id'])

div_result = soup.find_all('a', 'yt-uix-tile-link')
for div in div_result:
    print(youtube_url + div['href'], div.string)