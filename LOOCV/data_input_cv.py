# encoding=utf-8
import random
import pickle
import numpy as np
from  hyperparams import Hyperparams as params

random.seed(params.static_random_seed)
neg_pos_ratio = params.neg_pos_ratio
train_val_ratio = params.train_val_ratio


class DataLoader:
    def __init__(self, use_side_info=False):
        with open('../data_processing/data.pkl', 'rb') as file:
            pos_set, neg_set = pickle.load(file)
        with open('../data_processing/matrix.npy', 'rb') as file:
            matrix = np.load(file)

        if use_side_info:
            self.u_feature = np.load('../data_processing/u_feature.npy')
            self.v_feature = np.load('../data_processing/v_feature.npy')

        self.matrix = matrix
        self.pos_set = pos_set
        self.neg_set = neg_set
        self.pos_size = len(pos_set)
        self.train_set = self.pos_set + self.neg_set  # initializer

    def coor_to_sample(self, batch, use_sise_info=False):
        XL_batch = []
        XR_batch = []
        Y_batch = []
        for i, j, l in batch:
            temp = self.matrix[i][j]
            self.matrix[i][j] = 0
            XL_batch.append(self.matrix[i])
            XR_batch.append(self.matrix[:, j])
            self.matrix[i][j] = temp
            Y_batch.append(l)
        XL_batch = np.array(XL_batch)
        XR_batch = np.array(XR_batch)
        Y_batch = np.array(Y_batch).reshape((-1, 1))

        if use_sise_info is not True:
            return XL_batch, XR_batch, Y_batch
        else:
            u_feature_batch = []
            v_feature_batch = []
            for i, j, l in batch:
                u_feature_batch.append(self.u_feature[i])
                v_feature_batch.append(self.v_feature[j])
            U_batch = np.stack(u_feature_batch, axis=0)
            V_batch = np.stack(v_feature_batch, axis=0)
            return XL_batch, U_batch, XR_batch, V_batch, Y_batch

    def shuffle(self):
        random.shuffle(self.train_set)

    def leave_one_out(self, id):
        assert id >= 0 and id <= len(self.pos_set)

        neg_size = (self.pos_size - 1) * neg_pos_ratio
        neg_set = self.neg_set
        random.shuffle(neg_set)
        neg_set = neg_set[:neg_size]

        train_set = neg_set + self.pos_set[:id] + self.pos_set[id:]
        self.train_set = train_set
        self.train_size = len(train_set)
        self.val_set = [self.pos_set[id]]
        self.val_size = 1

    def sample_a_col(self, col_id):
        cols = []
        for i, x in enumerate(self.matrix[:, col_id]):
            cols.append((i, col_id, x))
        return cols


if __name__ == '__main__':
    dl = DataLoader()
    # print(dl.train_set)
    dl.shuffle()
