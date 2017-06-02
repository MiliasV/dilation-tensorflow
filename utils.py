# weight_value_tuples = [(t[0], np.transpose(t[1], (2, 3, 1, 0)) if len(np.shape(t[1]))==4 else t[1]) for t in weight_value_tuples]

import numpy as np
from keras.layers import Permute, Reshape, Activation
#import numba


# import pickle
# my_dict = {}
# for v in weight_value_tuples:
#     name = v[0].name
#     value = np.array(v[1])
#     my_dict[name] = value
# with open('data/pretrained_conv_channel_first.pickle', 'wb') as dump_file:
#     pickle.dump(my_dict, dump_file)


# with open('data/pretrained_conv_channel_first.pickle', 'rb') as f:
#     pretrained_theano = pickle.load(f)
#
# # convert to channel last
# dict_conv_channels_last = {}
# for k, v in pretrained_theano.items():
#     if len(v.shape) == 4:
#         v = np.transpose(v, axes=(2, 3, 1, 0))
#     dict_conv_channels_last[k] = v
# with open('data/pretrained_conv_channels_last.pickle', 'wb') as f:
#     pickle.dump(dict_conv_channels_last, f)
#
# dict_corr_channels_last = {}
# for k, v in dict_conv_channels_last.items():
#     if len(v.shape) == 4:
#         v = convert_kernel(v)
#     dict_corr_channels_last[k] = v
# with open('data/pretrained_corr_channels_last.pickle', 'wb') as f:
#     pickle.dump(dict_corr_channels_last, f)

# this function is the same as the one in the original repository
# basically it performs upsampling for datasets having zoom > 1
# @numba.jit(nopython=True)
def interp_map(prob, zoom, width, height):
    zoom_prob = np.zeros((prob.shape[0], height, width), dtype=np.float32)
    for c in range(prob.shape[0]):
        for h in range(height):
            for w in range(width):
                r0 = h // zoom
                r1 = r0 + 1
                c0 = w // zoom
                c1 = c0 + 1
                rt = float(h) / zoom - r0
                ct = float(w) / zoom - c0
                v0 = rt * prob[c, r1, c0] + (1 - rt) * prob[c, r0, c0]
                v1 = rt * prob[c, r1, c1] + (1 - rt) * prob[c, r0, c1]
                zoom_prob[c, h, w] = (1 - ct) * v0 + ct * v1
    return zoom_prob


def softmax(x, restore_shape=True):
    """
    Softmax activation for a tensor x. No need to unroll the input first.

    :param x: x is a tensor with shape (None, channels, h, w)
    :param restore_shape: if False, output is returned unrolled (None, h * w, channels)
    :return: softmax activation of tensor x
    """
    _, c, h, w = x._keras_shape
    x = Permute(dims=(2, 3, 1))(x)
    x = Reshape(target_shape=(h * w, c))(x)

    x = Activation('softmax')(x)

    if restore_shape:
        x = Reshape(target_shape=(h, w, c))(x)
        x = Permute(dims=(3, 1, 2))(x)

    return x