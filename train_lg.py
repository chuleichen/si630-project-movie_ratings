from re import A
import torch
import torch.nn as nn
from torch import optim 
import numpy as np
from tqdm import tqdm
import json 
import sklearn.metrics
import argparse

argparser = argparse.ArgumentParser()
argparser.add_argument(
    "--threshold",
    type=float,
    required=False)
argparser.add_argument(
    "--rating",
    action='store_true', 
    required=False)
argparser.add_argument(
    "--popularity",
    action='store_true', 
    required=False)
argparser.add_argument(
    "--num_epoch",
    type=int,
    default=50,
    required=False
)
argparser.add_argument(
    "--lr",
    type=float,
    default=0.001,
    required=False
)

args = argparser.parse_args()
threshold = args.threshold
if args.rating:
    region = 'rating'
    threshold = 6.5
else:
    region = 'popularity'
    threshold = 20
num_epoch = args.num_epoch
lr = args.lr

class LogisticRegression(nn.Module):
    def __init__(self, num_tokens, num_class):
        super(LogisticRegression,self).__init__()
        self.linear = nn.Linear(num_tokens, num_class)   

    def forward(self, x):
        return torch.log_softmax(self.linear(x),dim=1)

# read the data
print("reading train data")
with open('matrix_train_data.json','r') as f:
    data = f.read()
    data = json.loads(data)
    train_x = data['data']
    train_y_origin = data[region]
    train_y = []
    for y in train_y_origin:
        if y > threshold:
            train_y.append([1])
        else:
            train_y.append([0])
print('reading test data')
with open('matrix_test_data.json','r') as f:
    data = f.read()
    data = json.loads(data)
    test_x = data['data']
    test_y_origin = data[region]
    test_y = []
    for y in test_y_origin:
        if y > threshold:
            test_y.append(1)
        else:
            test_y.append(0)

# define the model
logistic_model=LogisticRegression(len(train_x[0]), 2)
loss_function = nn.NLLLoss()
optimizer = optim.SGD(logistic_model.parameters(), lr = lr)

loss_acc = 0

for epoch in range(num_epoch):
    print("begin epoch", epoch + 1)
    # for movie_num in tqdm(range(6000)):
    for movie_num in range(6000):

        logistic_model.zero_grad()

        log_probs = logistic_model(torch.FloatTensor([train_x[movie_num]]))

        loss = loss_function(log_probs, torch.LongTensor(train_y[movie_num]))
        loss.backward()
        optimizer.step()
        loss_acc += loss.item()

    print("loss after epoch", epoch+1, ":", loss_acc)
    loss_acc = 0

print('start test')
test_result = []
acc = 0
with torch.no_grad():
    # for movie_num in tqdm(range(1000)):
    for movie_num in range(1000):
        pred_y = logistic_model(torch.FloatTensor([test_x[movie_num]]))
        if pred_y[0][0] > pred_y[0][1]:
            result = 0
        else:
            result = 1
        test_result.append(result)
        if result == test_y[movie_num]:
            acc += 1
f1 = sklearn.metrics.f1_score(test_result, test_y[0:1000])
print('F-1 score =', f1)
print('Accuracy:', acc/1000)