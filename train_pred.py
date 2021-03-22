import csv 
import math
import re 
import sklearn.metrics
import numpy as np
from collections import Counter, defaultdict 

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
    for i in range(num_step):
        beta += learning_rate * compute_gradient(beta, x[i], y[i])
        if i % 100 == 0 or i == 999:
            print('log_likelihood_' + str(i), '=',  log_likelihood(x, y, beta))
    return beta 

def predict(beta, x):
    betaTx = 0
    for i in range(len(beta)):
        betaTx += beta[i]*x[i]
    if betaTx > 0.5:
        return '1.0'
    else:
        return '0.0'

x = np.array(x_count)
y = np.array(y) 
beta = logistic_regression(x, y, 0.0001, 1000)
print(beta) 

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