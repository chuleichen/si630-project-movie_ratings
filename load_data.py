import json
from tqdm import tqdm
import re 
from nltk.tokenize import RegexpTokenizer
from collections import Counter

stopwords = ["i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves", "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", "with", "about", "against", "between", "into", "through", "during", "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now"]

genres_dict = {28:0, 12:1, 16:2, 35:3, 80:4, 99:5, 18:6, 10751:7, 14:8, 36:9, 27:10, 10402:11, 9648:12, 10749:13, 878:14, 10770:15, 53:16, 10752:17, 37:18}

param_current = 1
param_before = 1
param_after = 1

tokens_file_name = 'tokens.txt'

def token_lower(message):
    tokenizer = RegexpTokenizer(r'[a-z]+')
    words = tokenizer.tokenize(message)
    return words

def load_data(movies_all, set_file_name, data_type, matrix_file_name):

    # load data
    data = []
    for line in open(data_type+"_data.jsonl", "r"):
        data.append(json.loads(line))
    print("Loaded {} {} conversations".format(len(data), data_type))
    movies_now = {}
    # parsing
    print("Start parsing...")

    with open(tokens_file_name, 'r') as f:
        line = f.readline()
        tokens_list = line.split(' ')
    # iterate all dialogues
    for dialogue in tqdm(data):
        # copy movie information to the set
        if dialogue['movieMentions'] == []:
            continue
        for movie_id in dialogue['movieMentions'].keys():
            if movie_id in movies_now.keys():
                continue
            try:
                if movies_all[movie_id] != 'failed':
                    movies_now[movie_id] = movies_all[movie_id]
            except:
                continue

        # iterate all messages
        for i in range(len(dialogue['messages'])):
            current_message = dialogue['messages'][i]['text']
            num_movie_mention = current_message.count('@')

            # if no movies mentioned in the message, skip it to avoid dubble count
            if num_movie_mention == 0:
                continue

            # otherwise, include all the messages that do not mention other movies before and after the current message
            words = current_message.split(' ')
            movie_ids = []
            patterns = '[0-9]+'
            for word in words:
                if '@' in word:
                    id_temp = re.search(patterns, word)
                    if id_temp is None:
                        continue
                    if movies_all[id_temp[0]] != 'failed':
                        movie_ids.append(id_temp[0])
            if len(movie_ids) == 0:
                continue
            
            tokens = token_lower(current_message.lower())
            for id in movie_ids:
                for token in tokens:
                    if token in stopwords:
                        continue 
                    elif token not in tokens_list:
                        tokens_list.append(token)
                    movies_now[id]['messages']['current'].append(token) 

            # look for messages before current messages
            current_index = i
            messages = []
            while current_index > 0:
                current_index -= 1
                num_movie = dialogue['messages'][current_index]['text'].count('@')
                if num_movie == 0:
                    messages.append(dialogue['messages'][current_index]['text'])
                else:
                    break
            for message in messages:
                tokens = token_lower(message.lower())
                for id in movie_ids:
                    for token in tokens:
                        if token in stopwords:
                            continue
                        elif token not in tokens_list:
                            tokens_list.append(token)
                        movies_now[id]['messages']['before'].append(token)
            
            # look for messages after current messages
            messages = []
            current_index = i
            while current_index < len(dialogue['messages']) - 1:
                current_index += 1
                num_movie = dialogue['messages'][current_index]['text'].count('@')
                if num_movie == 0:
                    messages.append(dialogue['messages'][current_index]['text'])
                else:
                    break
            for message in messages:
                tokens = token_lower(message.lower())
                for id in movie_ids:
                    for token in tokens:
                        if token in stopwords:
                            continue
                        elif token not in tokens_list:
                            tokens_list.append(token)
                        movies_now[id]['messages']['after'].append(token) 

        # iterate message tags
        questions = 'respondentQuestions'
        if dialogue[questions] is not dict:
            questions = 'initiatorQuestions'
            if dialogue[questions] is not dict:
                continue
        for movie_id in dialogue[questions].keys():
            if movies_now[movie_id] == 'failed':
                continue
            suggest = dialogue[questions][movie_id]['suggested']
            seen = dialogue[questions][movie_id]['seen']
            liked = dialogue[questions][movie_id]['liked']
            movies_now[movie_id]['suggested'] += suggest
            movies_now[movie_id]['seen'] += seen
            movies_now[movie_id]['liked'] += liked

    # create Counter
    for movie in movies_now.keys():
        messages = movies_now[movie]['messages']
        messages['current'] = Counter(messages['current'])
        messages['before'] = Counter(messages['before'])
        messages['after'] = Counter(messages['after'])

    with open(set_file_name,'w') as f:
        dumped_cache = json.dumps(movies_now)
        f.write(dumped_cache)  

    # update tokens
    with open(tokens_file_name, 'w') as f:
        for token in tokens_list:
            f.write(token)
            f.write(' ')

    # Create the matrix
    print()
    print('Creating data matrix')
    data_matrix = []
    output_popularity = []
    output_rating = []
    for movie in tqdm(movies_now.keys()):
        movie_data = []
        movie_now = movies_now[movie] 
        for genre in genres_dict.keys():
            flag = 0
            for genre_temp in movie_now['genres']:
                if genre_temp['id'] == genre:
                    flag = 1
                    break
            if flag == 1:
                movie_data.append(1)
            else: movie_data.append(0)
        movie_data.append(movie_now['num_language'])
        for token in tokens_list:
            weight = 0
            weight += param_current * movie_now['messages']['current'][token]
            weight += param_before * movie_now['messages']['before'][token]
            weight += param_after * movie_now['messages']['after'][token]
            movie_data.append(weight)
        output_popularity.append(movie_now['populatity'])
        output_rating.append(movie_now['rating'])
        data_matrix.append(movie_data)
    
    print()
    print('Writing data')
    # write the matrix
    with open(matrix_file_name, 'w') as f:
        f.write(str(len(data_matrix)))
        f.write('\n')
        for line in data_matrix:
            for num in line:
                f.write(str(num))
                f.write(' ')
            f.write('\n')
        for num in output_popularity:
            f.write(str(num))
            f.write(' ')
        f.write('\n')
        for num in output_rating:
            f.write(str(num))
            f.write(' ')
        f.write('\n')
        for token in tokens_list:
            f.write(token)
            f.write(' ')
        f.write('\n')

movie_cache_file_name = 'movies.json'
train_set_file_name = 'movies_train.json'
test_set_file_name = 'movies_test.json'
matrix_train_file_name = 'matrix_train.txt'
matrix_test_file_name = 'matrix_test.txt'

cache_file = open(movie_cache_file_name,'r', encoding='utf-8')
cache = cache_file.read()
movies_all = json.loads(cache)
cache_file.close()

# load_data(movies_all=movies_all, set_file_name=train_set_file_name, data_type='train', matrix_file_name=matrix_train_file_name)
load_data(movies_all=movies_all, set_file_name=test_set_file_name, data_type='test', matrix_file_name=matrix_test_file_name)
