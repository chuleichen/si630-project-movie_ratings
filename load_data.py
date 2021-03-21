import json
from tqdm import tqdm
import re 

def load_data(movies_all, set_file_name, data_type):

    # load data
    data = []
    for line in open(data_type+"_data.jsonl", "r"):
        data.append(json.loads(line))
    print("Loaded {} {} conversations".format(len(data), data_type))
    movies_now = {}
    # parsing
    print("Start parsing...")

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

            for id in movie_ids:
                    movies_now[id]['messages']['current'].append(current_message) 

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
                for id in movie_ids:
                    movies_now[id]['messages']['before'].append(message)
            
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
                for id in movie_ids:
                    movies_now[id]['messages']['after'].append(message) 

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

    with open(set_file_name,'w') as f:
        dumped_cache = json.dumps(movies_now)
        f.write(dumped_cache)   

movie_cache_file_name = 'movies.json'
train_set_file_name = 'movies_train.json'
test_set_file_name = 'movies_test.json'

cache_file = open(movie_cache_file_name,'r', encoding='utf-8')
cache = cache_file.read()
movies_all = json.loads(cache)
cache_file.close()

load_data(movies_all=movies_all, set_file_name=train_set_file_name, data_type='train')
load_data(movies_all=movies_all, set_file_name=test_set_file_name, data_type='test')
