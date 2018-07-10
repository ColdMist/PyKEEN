# -*- coding: utf-8 -*-
import torch
import torch.autograd
import torch.nn as nn

from utilities.constants import EMBEDDING_DIM, MARGIN_LOSS, NUM_ENTITIES, NUM_RELATIONS


class TransE(nn.Module):

    def __init__(self, config):
        super(TransE, self).__init__()
        # A simple lookup table that stores embeddings of a fixed dictionary and size

        num_entities = config[NUM_ENTITIES]
        num_relations = config[NUM_RELATIONS]
        self.embedding_dim = config[EMBEDDING_DIM]
        margin_loss = config[MARGIN_LOSS]

        self.entities_embeddings = nn.Embedding(num_entities, self.embedding_dim)
        self.relation_embeddings = nn.Embedding(num_relations, self.embedding_dim**2)
        self.margin_loss = margin_loss
        self.criterion = nn.MarginRankingLoss(margin=self.margin_loss, size_average=False)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    def compute_loss(self, pos_score, neg_score):
        """

        :param pos_score:
        :param neg_score:
        :return:
        """
        y = torch.tensor([1], dtype=torch.float, device=self.device)
        pos_score = pos_score.unsqueeze(0)
        neg_score = neg_score.unsqueeze(0)
        pos_score = torch.tensor(pos_score, dtype=torch.float, device=self.device)
        neg_score = torch.tensor(neg_score, dtype=torch.float, device=self.device)
        loss = self.criterion(pos_score, neg_score, y)

        return loss

    def calc_score(self, h_emb, r_emb, t_emb):
        """

        :param h_emb:
        :param r_emb:
        :param t_emb:
        :return:
        """
        # TODO: - torch.abs(h_emb + r_emb - t_emb)
        # Compute score and transform result to 1D tensor
        W = r_emb.view(-1, self.embedding_dim, self.embedding_dim)

        score = torch.bmm(torch.transpose(h_emb, 1, 2), W)  # h^T W
        score = torch.bmm(score, t_emb)  # (h^T W) h
        score = score.view(-1, 1)

        return score

    def predict(self, triple):
        """

        :param head:
        :param relation:
        :param tail:
        :return:
        """
        triple = torch.tensor(triple, dtype=torch.long, device=self.device)
        head, relation, tail = triple

        head_emb = self.entities_embeddings(head)
        relation_emb = self.relation_embeddings(relation)
        tail_emb = self.entities_embeddings(tail)

        score = self.calc_score(h_emb=head_emb, r_emb=relation_emb, t_emb=tail_emb)

        return score.detach().numpy()

    def forward(self, pos_exmpl, neg_exmpl):
        """

        :param pos_exmpl:
        :param neg_exmpl:
        :return:
        """

        pos_h, pos_r, pos_t = pos_exmpl
        neg_h, neg_r, neg_t, = neg_exmpl

        pos_h_emb = self.entities_embeddings(pos_h)
        pos_r_emb = self.relation_embeddings(pos_r)
        pos_t_emb = self.entities_embeddings(pos_t)

        neg_h_emb = self.entities_embeddings(neg_h)
        neg_r_emb = self.relation_embeddings(neg_r)
        neg_t_emb = self.entities_embeddings(neg_t)

        pos_score = self.calc_score(h_emb=pos_h_emb, r_emb=pos_r_emb, t_emb=pos_t_emb)
        neg_score = self.calc_score(h_emb=neg_h_emb, r_emb=neg_r_emb, t_emb=neg_t_emb)

        loss = self.compute_loss(pos_score=pos_score, neg_score=neg_score)

        return loss
