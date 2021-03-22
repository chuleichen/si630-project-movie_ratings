import math
import numpy as np
from tqdm import tqdm
import sklearn.metrics

def sigmoid(array):
    result = 1/(np.exp(-array) + 1)
    return result

def log_likelihood(x, y, beta):
    ll = 0
    for i in range(len(y)):
        betaTx = 0
        for j in range(len(x[i])):
            betaTx += beta[j]*x[i][j]
        ll += y[i]*betaTx - math.log(1+math.exp(betaTx))
    return ll 

def compute_gradient(beta, x, y):
    sig = sigmoid(beta * x)
    result = (y - sig) * x
    return result

def logistic_regression(x, y, learning_rate, num_step):
    beta = np.zeros(len(x[0]))
    for i in tqdm(range(num_step)):
        beta += learning_rate * compute_gradient(beta, x[i], y[i])
        # if i % 500 == 0:
        #     print('log_likelihood_' + str(i), '=',  log_likelihood(x, y, beta))
    return beta 

def predict(beta, x):
    betaTx = 0
    for i in range(len(beta)):
        betaTx += beta[i]*x[i]
    if betaTx > 0.5:
        return 1
    else:
        return 0

# reading train data
threshold = 5
movie_data = []
popularity = []
rating = []
with open('matrix_train.txt', 'r') as f:
    print('    Reading movie data')
    num_line = int(f.readline())
    for i in range(num_line):
        line = f.readline()
        line_data = line.split(' ')
        line_temp = []
        for num in line_data[:-1]:
            temp = float(num)
            line_temp.append(temp)
        movie_data.append(line_temp)
    print('    Reading popularity')
    line = f.readline()
    popularity_line = line.split(' ')
    for num in popularity_line[:-1]:
        temp = float(num)
        popularity.append(temp)
    print('    Reading rating')
    line = f.readline()
    rating_line = line.split(' ')
    for num in rating_line[:-1]:
        temp = float(num)
        rating.append(temp)
print('Finish reading train data')
y = []
for num in rating:
    if num >= threshold:
        y.append(1)
    else:
        y.append(0)

x = np.array(movie_data)
y = np.array(y) 
beta = logistic_regression(x, y, 0.0001, 1000)

print('Reading test data')
movie_data_test = []
popularity_test = []
rating_test = []
with open('matrix_test.txt', 'r') as f:
    print('    Reading movie data')
    num_line = int(f.readline())
    for i in range(num_line):
        line = f.readline()
        line_data = line.split(' ')
        line_temp = []
        for num in line_data[:-1]:
            temp = float(num)
            line_temp.append(temp)
        movie_data_test.append(line_temp)
    print('    Reading popularity')
    line = f.readline()
    popularity_line = line.split(' ')
    for num in popularity_line[:-1]:
        temp = float(num)
        popularity_test.append(temp)
    print('Reading rating')
    line = f.readline()
    rating_line = line.split(' ')
    for num in rating_line[:-1]:
        temp = float(num)
        rating_test.append(temp)

print('Start predicting')
step = 0
y_true = []
for num in rating_test:
    if step == 100:
        break
    if num >= threshold:
        y_true.append(1)
    else:
        y_true.append(0)
    step += 1

step = 0
y_pred = []
for data in tqdm(movie_data_test):
    if step == 100: 
        break
    temp = predict(beta, data)
    y_pred.append(temp)
    step += 1

f1 = sklearn.metrics.f1_score(y_true, y_pred)
print('F1 score =', f1)

'''
# dev set and calculate F1
y_true = []
y_pred = []
for text in dev:
    words = tokenize(text[2])
    count_dict = defaultdict(int)
    for word in words:
        if word in count_dict.keys():
            count_dict[word] += 1
        else:
            count_dict[word] = 1
    temp = []
    for v in x_dict.keys():
        temp.append(count_dict[v])
    classify_result = predict(beta, temp)
    if text[1] == '1.0':
        y_true.append(1)
    else: 
        y_true.append(0)
    if classify_result == '1.0':
        y_pred.append(1)
    else:
        y_pred.append(0)
print(sklearn.metrics.f1_score(y_true, y_pred))
'''