# -*- coding: utf-8 -*-
import os
import tarfile
import pickle
import numpy as np
import PIL

import tensorflow as tf

import tensorflow.contrib.slim as slim

import tensorflow.contrib.slim.nets as nets

from six.moves.urllib.request import urlretrieve


def get_file_name(path):

    filenames = os.listdir(path)
    path_filenames = []
    filename_list = []

    for file in filenames:

        if 'sift' not in file:

            if not file.startswith('.'):
                path_filenames.append(os.path.join(path, file))
                filename_list.append(file)

    return path_filenames


sess = tf.InteractiveSession()

image = tf.Variable(tf.zeros((299, 299, 3)))


def network(image, reuse):

    preprocessed = tf.multiply(tf.subtract(tf.expand_dims(image, 0), 0.5), 2.0)
    arg_scope = nets.inception.inception_v3_arg_scope(weight_decay=0.0)

    with slim.arg_scope(arg_scope):

        logits, end_points = nets.inception.inception_v3(
            preprocessed, 1001, is_training=False, reuse=reuse)

        logits = logits[:, 1:]

        probs = tf.nn.softmax(logits)

    return logits, probs, end_points


logits, probs, end_points = network(image, reuse=False)

checkpoint_filename = "./inception_v3.ckpt"

if not os.path.exists(checkpoint_filename):
    inception_tarball, _ = urlretrieve("http://download.tensorflow.org/models/inception_v3_2016_08_28.tar.gz")

    tarfile.open(inception_tarball, 'r:gz').extractall("./")


restore_vars = [var for var in tf.global_variables() if var.name.startswith('InceptionV3/')]

saver = tf.train.Saver(restore_vars)

saver.restore(sess, "./inception_v3.ckpt")


def get_feature(img, feature_layer_name):

    p, feature_values = sess.run([probs, end_points], feed_dict={image: img})

    return feature_values[feature_layer_name].squeeze()


image_urls = get_file_name("/home/linlinan/lln_test/")

images = []

for idx, img_path in enumerate(image_urls):

    img = PIL.Image.open(img_path)

    img = img.resize((299, 299))

    images.append(img)

layer = 'PreLogits'

features = []

# 这里是我添加

test_features = []

for img in images:

    # 这里是对每一副图片做了归一化操作
    img = (np.asarray(img)/255.0).astype(np.float32)

    feature = get_feature(img, layer)

    features.append(feature)

feature_vectors = np.stack(features)

print(feature_vectors.shape)

with open('/home/linlinan/lln_features/test.pkl', 'wb') as f:
    pickle.dump(feature_vectors, f)


