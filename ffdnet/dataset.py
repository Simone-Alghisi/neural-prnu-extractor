""" dataset.py
Dataset related functions

Copyright (C) 2018, Matias Tassano <matias.tassano@parisdescartes.fr>

This program is free software: you can use, modify and/or
redistribute it under the terms of the GNU General Public
License as published by the Free Software Foundation, either
version 3 of the License, or (at your option) any later
version. You should have received a copy of this license along
this program. If not, see <http://www.gnu.org/licenses/>.
"""
import os
import os.path
import random
import glob
import numpy as np
import cv2
import h5py
import torch
import torch.utils.data as udata
from tqdm import tqdm
from ffdnet.utils.data_utils import normalize

def img_to_patches(img, win, stride=1):
  r"""Converts an image to an array of patches.

  Args:
    img: a numpy array containing a CxHxW RGB (C=3) or grayscale (C=1)
      image
    win: size of the output patches
    stride: int. stride
  """
  k = 0
  endc = img.shape[0]
  endw = img.shape[1]
  endh = img.shape[2]
  patch = img[:, 0:endw-win+0+1:stride, 0:endh-win+0+1:stride]
  total_pat_num = patch.shape[1] * patch.shape[2]
  res = np.zeros([endc, win*win, total_pat_num], np.float32)
  for i in range(win):
    for j in range(win):
      patch = img[:, i:endw-win+i+1:stride, j:endh-win+j+1:stride]
      res[:, k, :] = np.array(patch[:]).reshape(endc, total_pat_num)
      k = k + 1
  return res.reshape([endc, win, win, total_pat_num])

def prepare_data(data_path,
         val_data_path,
         patch_size,
         stride,
         train_file,
         val_file,
         total_patches,
         gray_mode=False):
  r"""Builds the training and validations datasets by scanning the
  corresponding directories for images and extracting	patches from them.

  Args:
    data_path: path containing the training image dataset
    val_data_path: path containing the validation image dataset
    patch_size: size of the patches to extract from the images
    stride: size of stride to extract patches
    total_patches: total number desired of patches 
    max_num_patches: maximum number of patches to extract
    aug_times: number of times to augment the available data minus one
    gray_mode: build the databases composed of grayscale patches
  """
  # training database
  print('> Training database')
  types = ('*.bmp', '*.png', '*.jpg')
  files = []
  for tp in types:
    files.extend(glob.glob(os.path.join(data_path, tp)))
  files.sort()

  traindbf = 'dataset/'+ train_file
  valdbf = 'dataset/' + val_file

  train_num = 0
  val_num = 0
  i = 0
  n_files = len(files)
  patches_per_file = total_patches//n_files
  reminder = total_patches%n_files
  t_file = tqdm(total=n_files)
  while i < len(files):
    with h5py.File(traindbf, 'a') as h5f:
      imgor = cv2.imread(files[i])
      # h, w, c = img.shape
      img = imgor
      if not gray_mode:
        # CxHxW RGB image
        img = (cv2.cvtColor(img, cv2.COLOR_BGR2RGB)).transpose(2, 0, 1)
      else:
        # CxHxW grayscale image (C=1)
        img = img[:, :, 1]
        img = np.expand_dims(img, 0)
      img = normalize(img)
      patches = img_to_patches(img, win=patch_size, stride=stride)
      np.random.shuffle(patches)
      nx = 0
      n_patches = patches.shape[3]
      already_picked = False
      while nx < n_patches and nx < patches_per_file:
        data = patches[:, :, :, nx]
        h5f.create_dataset(str(train_num), data=data)
        train_num += 1
        if reminder > 0 and not already_picked:
          reminder -= 1
          already_picked = True
        else:
          nx += 1
      i += 1
      t_file.update(1)
  t_file.close()

  # validation database
  print('\n> Validation database')
  if val_data_path is None:
    print('\n> No')
  else:
    files = []
    for tp in types:
      files.extend(glob.glob(os.path.join(val_data_path, tp)))
    files.sort()
    h5f = h5py.File(valdbf, 'w')
    val_num = 0
    for i, item in tqdm(enumerate(files)):
      img = cv2.imread(item)
      if not gray_mode:
        # C. H. W, RGB image
        img = (cv2.cvtColor(img, cv2.COLOR_BGR2RGB)).transpose(2, 0, 1)
      else:
        # C, H, W grayscale image (C=1)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = np.expand_dims(img, 0)
      img = normalize(img)
      h5f.create_dataset(str(val_num), data=img)
      val_num += 1
    h5f.close()

  print('\n> Total')
  print('\ttraining set, # samples %d, # patches %d' % (train_num, train_patches))
  print('\tvalidation set, # samples %d \n' % val_num)

class Dataset(udata.Dataset):
  r"""Implements torch.utils.data.Dataset
  """

  r"""Initialize the Dataset

  Args:
    dbf: path containing the dataset file
    train: boolean flag which describes whether the dataset is the training set
    gray_mode: boolean flag which describes whether the dataset contains gray images
    shuffle: boolean flag which describes whether the dataset requires to be shuffled
  """
  def __init__(self, dbf, train=True, gray_mode=False, shuffle=False):
    super(Dataset, self).__init__()
    self.train = train
    self.gray_mode = gray_mode
    self.dbf = dbf

    h5f = h5py.File(self.dbf, 'r')
    self.keys = list(h5f.keys())

    if shuffle:
      random.shuffle(self.keys)
    h5f.close()

  r"""Returns the number of elements in the dataset
  """
  def __len__(self):
    return len(self.keys)

  r"""Returns the element at a given position in the dataset

  Args:
    index: index of the element to be returned
  """
  def __getitem__(self, index):
    h5f = h5py.File(self.dbf, 'r')
    key = self.keys[index]
    data = np.array(h5f[key])
    h5f.close()
    return torch.Tensor(data)