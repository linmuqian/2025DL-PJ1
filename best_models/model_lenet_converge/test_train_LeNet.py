import mynn as nn
from draw_tools.plot import plot

import numpy as np
from struct import unpack
import gzip
import matplotlib.pyplot as plt
import pickle

np.random.seed(309)

train_images_path = r'dataset/MNIST/train-images-idx3-ubyte.gz'
train_labels_path = r'/MNIST/train-labels-idx1-ubyte.gz'

# read training images
with gzip.open(train_images_path, 'rb') as f:
    magic, num, rows, cols = unpack('>4I', f.read(16))
    train_imgs = np.frombuffer(f.read(), dtype=np.uint8).reshape(num, 28, 28)

# read training labels
with gzip.open(train_labels_path, 'rb') as f:
    magic, num = unpack('>2I', f.read(8))
    train_labs = np.frombuffer(f.read(), dtype=np.uint8)

# data preprocessing: pad 28x28 images to 32x32 and normalize
train_imgs = np.expand_dims(train_imgs, axis=1)  # convert to (N, 1, 28, 28)
train_imgs = np.pad(train_imgs, ((0, 0), (0, 0), (2, 2), (2, 2)), mode='constant')  # convert to (N, 1, 32, 32)
train_imgs = train_imgs.astype(np.float32) / 255.0  # normalize to [0,1]

# choose 10000 samples from train set as validation set.
idx = np.random.permutation(np.arange(num))
train_imgs = train_imgs[idx]
train_labs = train_labs[idx]
valid_imgs = train_imgs[:500]
valid_labs = train_labs[:500]
train_imgs = train_imgs[10000:30000]
train_labs = train_labs[10000:30000]


model = nn.models.Model_LeNet(in_channels=1, num_classes=10)
loss_fn = nn.op.MultiCrossEntropyLoss(model=model, max_classes=10)
optimizer = nn.optimizer.Adam(init_lr=0.01, beta1=0.9, beta2=0.99, eps=1e-7, model=model)
scheduler = nn.lr_scheduler.MultiStepLR(optimizer=optimizer, milestones=[800, 2400, 4000], gamma=0.2)

runner = nn.runner.RunnerM_c(model, optimizer, nn.metric.accuracy, loss_fn, scheduler=scheduler, batch_size=64)

save_dir = r'best_models/model_lenet_converge'

runner.train([train_imgs, train_labs], [valid_imgs, valid_labs], num_epochs=5, log_iters=10, save_dir=save_dir)

_, axes = plt.subplots(1, 2)
axes.reshape(-1)
_.set_tight_layout(1)
plot(runner, axes)

import os
if not os.path.exists(save_dir):
    os.makedirs(save_dir)
image_path = os.path.join(save_dir, 'training_plot.png')
plt.savefig(image_path)

plt.show()
