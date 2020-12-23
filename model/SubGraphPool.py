import torch as t
import torch.nn as nn
import torch.nn.functional as F


class SubGraphAvgPool(nn.Module):

    def __init__(self, opt):
        super(SubGraphAvgPool, self).__init__()
        self.opt = opt
        self.now = 0  # 当前子树根节点
        self.pool = nn.AvgPool2d((opt.m+1, 1))

    def forward(self, h):
        # h 为前一层的树，大小为(n x p) 其中n为前一层的结点数

        m = self.opt.m
        conv_graph = self.generate_graph(m, h.shape[1])
        sub_graph = h[:, conv_graph, :]  # batch x (m+1) x new_tree_nodes x p

        output = self.pool(sub_graph.permute((0, 3, 1, 2))).squeeze()
        # batch x new_tree_nodes x features_out
        if len(output.shape) == 3:
            output = output.permute((0, 2, 1))
        else:
            output = output.unsqueeze(1)
        return output

    def generate_graph(self, m, num_nodes):
        now = 0
        graph = []
        while now * m + 1 < num_nodes:
            col = [now]
            col = col + [node for node in range(now * m + 1, now * m + 1 + m)]
            graph.append(t.tensor(col, dtype=t.long)[:, None])
            now += 1
        return t.cat(graph, dim=-1)

