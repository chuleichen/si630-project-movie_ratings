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
    default=6000,
    required=False
)
argparser.add_argument(
    "--lr",
    type=float,
    default=0.001,
    required=False
)

args = argparser.parse_args()
if args.rating:
    region = 'rating'
else:
    region = 'popularity'
num_epoch = args.num_epoch
lr = args.lr

# read the data
print("reading train data")
with open('matrix_train_data.json','r') as f:
    data = f.read()
    data = json.loads(data)
    train_x = data['data']
    train_y = data[region]

print('reading test data')
with open('matrix_test_data.json','r') as f:
    data = f.read()
    data = json.loads(data)
    test_x = data['data']
    test_y = data[region]

# define the model
model = nn.Sequential(
    nn.Linear(len(train_x[0]), 1),
    nn.Flatten(0, 1)
) 

loss_function = nn.MSELoss(reduction='sum')
optimizer = optim.RMSprop(model.parameters(), lr=lr)

# for movie_num in tqdm(range(num_epoch)):
for movie_num in range(num_epoch):

    y_pred = model(torch.FloatTensor(train_x))
    loss = loss_function(y_pred, torch.FloatTensor(train_y))
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    if movie_num % 10 == 9:
        print("Step", movie_num, "loss =", loss.item())

print('start test')
test_result = []

with torch.no_grad():
    # for movie_num in tqdm(range(1000)):
    for movie_num in range(1000):
        pred_y = model(torch.FloatTensor([test_x[movie_num]]))
        test_result.append(pred_y[0])

mse = sklearn.metrics.mean_squared_error(test_result, test_y[0:1000])
print('nn test mse =', mse)