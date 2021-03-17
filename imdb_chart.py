import pandas as pd
from pandas.io import json
import requests
from bs4 import BeautifulSoup
import sys

"""
Approach Followed

We will be scrapping the data using BeautifulSoup. After getting the page in
the HTML format we need to parse and get the values of the movies. 
We will store the results in a csv and python data frames to access the values
and columns. Further using the tags in html we parse the required data for 
each of the movies and store in the same csv on the row identifying the movie.

To read into, we use Dataframe and python pandas module to perform the operations
get the series of data. Finally we dump the result in the required format as the
fields are expected.
"""
class WebScrapper():
    def __init__(self, url, item_count):
        self.url = url
        self.item_count = item_count
        

    def get_urls(self):
        df = pd.DataFrame(columns= ['url'])
        page = requests.get(self.url)
        soup = BeautifulSoup(page.content, features='lxml')  
        movies = soup.find("tbody", class_="lister-list")
        movie_meta = movies.find_all('tr')
        
        for pt, item in enumerate(movie_meta):
            if(pt < int(self.item_count)):
                link_wrapper = item.find("td", class_="titleColumn")
                link_tag = link_wrapper.find("a",  href=True)
                link = link_tag['href']
                df = df.append({ 'url': 'https://www.imdb.com/' + str(link) }, ignore_index=True)
                
        df.to_csv('./movie_url_list.csv', index=True)

    def get_movie_meta(self):
        result = []
        df = pd.read_csv('./movie_url_list.csv')
        movie_url = df['url']
        for i, url in enumerate(movie_url):
            page = requests.get(url)
            soup = BeautifulSoup(page.content, features='lxml')
            
            title = ''
            movie_release_year = ''
            imdb_rating = ''
            summary = ''
            duration = ''
            genres = ''

            # get title and release year
            title_wrapper = soup.find("div", class_="title_wrapper")
            title_year = title_wrapper.find("h1").text.strip()
            title = title_year.split('(')[0].strip()
            movie_release_year = title_year.split('(')[1][:-1]
            
            # get duration and genre
            sub_text = title_wrapper.find("div", class_="subtext")
            duration = sub_text.find("time").text.strip()
            genre_tags = sub_text.find_all("a", text=True)
            for genre_tag in genre_tags[:-1]:
                genres += genre_tag.text.strip() + ' '
            genres = genres.rstrip()
            genres = genres.replace(" ", ", ")
            # get imdb
            imdb_rating = soup.find("span", itemprop="ratingValue").text.strip()
            # get summary
            summary = soup.find("div", class_="summary_text").text.strip()
            
            result.append({
                "title": title, 
                "movie_release_year": movie_release_year, 
                "imdb_rating": imdb_rating,
                "summary": summary,
                "duration": duration,
                "genre": genres
                })

        result = json.dumps(result)
        return result

url = sys.argv[1]
item_count = sys.argv[2]
WebScrapper = WebScrapper(url, item_count)
try: 
    WebScrapper.get_urls()
except Exception as e:
    print(e)
try:
    result_set = WebScrapper.get_movie_meta()
    df = pd.read_json(result_set)
    df.to_csv('./movie_records.csv', index=True)
    print(result_set)
except Exception as e:
    print(e)
