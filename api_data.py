import requests
import json
import csv
from tqdm import tqdm 
import time 
from api_keys import api_key

base_search_movie = 'https://api.themoviedb.org/3/search/movie'
base_movie = 'https://api.themoviedb.org/3/movie/'
cache_file_name = 'movies.json'

try:
    cache_file = open(cache_file_name,'r', encoding='utf-8')
    cache = cache_file.read()
    cache_dict = json.loads(cache)
    cache_file.close()
except:
    cache_dict = {}

step = 0
movie_dict = {}
lines = []

# read the file
with open('movies_with_mentions.csv', 'r') as f:
    reader = csv.reader(f)
    for line in reader:
        lines.append(line)

# start requests
for line in tqdm(lines):
    id = line[0]

    # chech if the movie is already in the dict
    if id in cache_dict.keys():
        if cache_dict[id] == 'failed':
            continue # comment this two lines to search the failed movies again
        if cache_dict[id] != 'failed':
            # add something here to reset the data
            continue
    if id == 'movieId':
        continue

    # parse movie title and year
    title = line[1]
    year = 0
    params = {
        'api_key':api_key,
        'query': title,
        'include_adult': True
    }
    if title[-5:-2].isdigit():
        year = title[-5:-1]
        title = title[:-7]
        params['year'] = year
        params['query'] = title

    # get the api id of the movie
    # try at most 5 times, if failed, print the error message
    try_flag = 0
    while try_flag <= 5:
        try: 
            response = requests.get(url=base_search_movie,params= params)
            try_flag = 6
        except:
            print("Retry searching movie id...")
            time.sleep(30)
            try_flag += 1
    result = response.json()

    # chech if there is search result
    try:
        api_id = result['results'][0]['id']
        populatity = result['results'][0]['popularity']
    except:
        
        # in case there is no result, search the movie without year
        # try at most 5 times, if failed, print the error message
        try:
            params = {
                'api_key':api_key,
                'query': title,
                'include_adult': True
            }
            try_flag = 0
            while try_flag <= 5:
                try: 
                    response = requests.get(url=base_search_movie,params= params)
                    try_flag = 6
                except:
                    print("Retry searching movie id without year...")
                    time.sleep(30)
                    try_flag += 1
            result = response.json()
            api_id = result['results'][0]['id']
            populatity = result['results'][0]['popularity']

        # if the movie still cannot be found, print the error message, and mark the movie as failed in the dict
        except:
            print('Movie', title, 'cannot be found.')
            cache_dict[id] = "failed"
            time.sleep(1)
            continue
    time.sleep(1)

    # start search for the detailed information of the movie
    # try at most 5 times, if failed, print the error message
    params = {
        'api_key': api_key
    }
    base_url = base_movie+str(api_id)
    try_flag = 0
    success = 0
    while try_flag <= 5:
        try: 
            response = requests.get(url=base_url, params=params)
            try_flag = 6
            success = 1
        except:
            print("Retry searching movie details...")
            time.sleep(30)
            try_flag += 1
    if success == 0:
        print('\n   Movie', title, 'cannot be found. Id is found here!')
        cache_dict[id] = "failed"
        time.sleep(1)
        continue
    result = response.json()

    # look for the information of the movie and write into the dict
    genres = result['genres']
    production_companies = []
    for company in result['production_companies']:
        production_companies.append({'id':company['id'], 'name':company['name']})
    num_language =len(result['spoken_languages'])
    rating = result['vote_average']
    movie_info = {
        'title': title,
        'year': year,
        'suggested': 0,
        'seen': 0,
        'liked': 0,
        'populatity': populatity,
        'genres': genres,
        'production_companies': production_companies,
        'num_language': num_language,
        'rating': rating,
        'messages': {'current':[], 'before':[], 'after':[]}
    }
    cache_dict[id] = movie_info
    time.sleep(1)

    # save the dict file every ten movies
    step += 1
    if step % 10 == 0:
        with open(cache_file_name,'w') as f:
            dumped_cache = json.dumps(cache_dict)
            f.write(dumped_cache)  

# save the dict file  
with open(cache_file_name,'w') as f:
    dumped_cache = json.dumps(cache_dict)
    f.write(dumped_cache)   