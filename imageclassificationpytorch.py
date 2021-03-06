# -*- coding: utf-8 -*-
"""ImageClassificationPytorch.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1FuataGbuEPrRfJQ_gioF2hMHLms_zxOl
"""

# Commented out IPython magic to ensure Python compatibility.
import matplotlib.pyplot as plt
import numpy as np

import torch
import torchvision
import torchvision.transforms as transforms
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

#initialise the CPU/GPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#prefer GPU over CPU as it can do parallel computations
#need to register to get GPU access on colab

print("Using device: %s" %device)

classes = ('plane', 'car', 'bird', 'cat', 'deer', 'dog', 'frog','horse','ship','truck')
epochs = 10   #number of total iterations
bs = 4  #batches -> train in batches of 4


# %matplotlib inline

#Data loading and pre-processing

transform = transforms.Compose(
    [transforms.ToTensor(),
     transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))]
) #mean, standard deviation = 0.5, makes it easier to train (from 0 - 1 to centered around 0.5)
#transform to tensor first as well, size 32*32*3

#preparing the training set

trainset = torchvision.datasets.CIFAR10(root = './data', train = True, download = True, transform = transform)
trainloader = torch.utils.data.DataLoader(trainset, batch_size = bs, shuffle = True, num_workers = 2)

#Preparing the testing set
testset = torchvision.datasets.CIFAR10(root = './data', train = False, download = True, transform = transform)
testloader = torch.utils.data.DataLoader(testset, batch_size = bs, shuffle = False, num_workers = 2)

"""
the following code is to display the images post transformation
"""

def imshow(img):
  img = img/2 + 0.5
  nping = img.numpy()
  plt.imshow(np.transpose(nping, (1,2,0)))
  plt.show()

#get random training iomages
dataiter = iter(trainloader)
images, labels = dataiter.next()

#show images
imshow(torchvision.utils.make_grid(images))
print(' '.join('%5s' % classes[labels[j]] for j in range(4)))

# Neural network model
class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        #convulutional layers
        self.conv1 = nn.Conv2d(3, 32, 3) # conv. kernel size of 3
        self.conv2 = nn.Conv2d(32, 64, 4) #32->64
        #pooling layers
        self.pool = nn.MaxPool2d(2,2) #taking max of values in a grid (pooling), reducing size
        #by factor of 4

        #linear layer needs flat layer input
        self.fc1 = nn.Linear(6*6*64, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84,10) #10 classes so output = 10

    def forward(self, x):

        #input layer -> conv layer -> max pooling -> conv layer -> max pool -> fc1 -> fc2 -> fc3 -> output

        # 32*32*3 into 30*30*32 (3 -> 32 due to convol (so from rgb, to 32 diff colors kindof))
        # the 32 -> 30 is by the windowing function due to convolution (kernel size 3)
        #then pool to 15*15*32  (pool reduces dimension by half, due to 2x2 pool size)
        x = self.pool(F.relu(self.conv1(x)))

        # 15*15*32 into 12*12*64 (15->12 due to kernel size 4)
        #then pool to 6*6*64
        x = self.pool(F.relu(self.conv2(x)))

        #flatten
        x = x.view(-1, 6*6*64) #reshape into matrix
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x

net = Net()
net.to(device) #assign CPU to this network

criterion = nn.CrossEntropyLoss()  #loss function
optimizer = optim.SGD(net.parameters(), lr=0.001, momentum = 0.9) #adam or SGD works
#choose whichever
#lr is learning rate, the bigger the faster it trains, prone to missing minimum
#SGD (stochastic gradient descent)
#adam is alternative to stochastic gradient descent
#momentum = momentum of finding the minimum

from torchsummary import summary
summary(net, input_size=(3, 32, 32))

#summarises network

print('Training...')

for epoch in range(epochs): #looping over the dataset multiple times, based on the pre-defined number of epochs

  running_loss = 0.0

  for i, data in enumerate(trainloader, 0): 
    #get the inputs; data is a list of [inputs, labels]
    inputs, labels = data[0].to(device), data[1].to(device)

    #zero the parameter gradients. We are using SGD
    optimizer.zero_grad()

    #forward + backward + optimise
    outputs = net(inputs)
    loss = criterion(outputs, labels)
    loss.backward()
    optimizer.step()

    ########

    #print statistics
    running_loss += loss.item()
    if i % 2000 == 1999: #print every 2000 mini batches
      print('[%d, %5d] loss: %.3f' % (epoch +1, i+1, running_loss/2000))

      running_loss = 0.0

print('Finished.')

#evaluating model
class_correct = list(0. for i in range(10))
class_total = list(0. for i in range(10))
with torch.no_grad():
    for data in testloader:
        images, labels = data[0].to(device), data[1].to(device)
        outputs = net(images)
        _, predicted = torch.max(outputs, 1)
        c = (predicted == labels).squeeze() #get rid of first dimension
        for i in range(bs):
            label = labels[i]
            class_correct[label] += c[i].item()
            class_total[label] += 1

print(np.array(class_correct)/np.array(class_total))
for i in range(10):
    print('Accuracy of %5s: %2d %%' % (
        classes[i], 100*class_correct[i]/class_total[i]
    ))