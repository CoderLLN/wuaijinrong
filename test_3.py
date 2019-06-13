# -*- coding: utf-8 -*-
import os
import tarfile

import matplotlib.pyplot as plt
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

# 这里是我添加
test_features.append(get_feature((np.asarray(images[51])/255.0).astype(np.float32), layer))
test_features_vectors = np.stack(test_features)

print("="*50)

print(feature_vectors.shape)


try:

    assert feature_vectors.shape == (532, 2048), 'shape mismatch!'

except Exception as ex:

    print(ex)


distance_euclidean = np.sum(np.power(test_features_vectors, 2), axis=1, keepdims=True) + np.sum(np.power(feature_vectors, 2),
                    axis=1, keepdims=True).T - 2*np.dot(test_features_vectors, feature_vectors.T)


print(distance_euclidean.shape)

order_euclidean = np.argsort(distance_euclidean[0])

print(order_euclidean.shape)


plt.figure(figsize=(8, 8))

for idx_sim, i in enumerate(order_euclidean):

    similay_img = images[i]

    # 这里需要注意plt的subplot是从1开始计数的
    plt.subplot(4, 4, idx_sim + 1)

    plt.axis("off")

    plt.imshow(similay_img)

    if idx_sim > 14:
        break


plt.show()



