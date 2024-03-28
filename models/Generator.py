import torch
import torch.nn as nn
from Utils.combine_vectors import combine_vectors




# LSTM ForGAN generator
class Generator(nn.Module):
    '''
    Generator Class
    Values:
        noise_dim: the dimension of the noise, a scalar
        cond_dim: the dimension of the condition, a scalar
        hidden_dim: the inner dimension, a scalar
    '''

    def __init__(self, cfg, mean, std):
        super(Generator, self).__init__()
        self.input_dim = cfg.z_dim + cfg.l
        self.cond_dim = cfg.l
        self.hidden_dim = cfg.hid_g
        self.output_dim = cfg.pred
        self.noise_dim = cfg.z_dim
        # predicting a single value, so the output dimension is 1
        self.mean = mean
        self.std = std
        # Add the modules

        self.lstm = nn.LSTM(input_size=self.cond_dim, hidden_size=self.hidden_dim, num_layers=1, dropout=0)
        # nn.init.xavier_normal_(self.lstm.weight)
        nn.init.xavier_normal_(self.lstm.weight_ih_l0)
        nn.init.xavier_normal_(self.lstm.weight_hh_l0)
        self.linear1 = nn.Linear(in_features=self.hidden_dim + self.noise_dim,
                                 out_features=self.hidden_dim + self.noise_dim)
        nn.init.xavier_normal_(self.linear1.weight)
        self.linear2 = nn.Linear(in_features=self.hidden_dim + self.noise_dim, out_features=self.output_dim)
        nn.init.xavier_normal_(self.linear2.weight)
        self.activation = nn.ReLU()

    def forward(self, noise, condition, h_0, c_0):
        '''
        Function for completing a forward pass of the generator:adding the noise and the condition separately
        '''
        # x = combine_vectors(noise.to(torch.float),condition.to(torch.float),2)
        condition = (condition - self.mean) / self.std
        out, (h_n, c_n) = self.lstm(condition, (h_0, c_0))
        out = combine_vectors(noise.to(torch.float), h_n.to(torch.float), dim=-1)
        out = self.linear1(out)
        out = self.activation(out)
        out = self.linear2(out)
        out = out * self.std + self.mean
        return out

