import torch
import torch.nn as nn
from torch.autograd import Variable
from torch.nn import functional
from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence



class ASReader(nn.Module):
    def __init__(self, vocab_size, embedding_dim, encoding_dim):
        super(ASReader, self).__init__()

        self.embedding_dim = embedding_dim
        self.encoding_dim = encoding_dim

        self.embedding_layer = nn.Embedding(vocab_size, embedding_dim)

        self.document_encoding = nn.GRU(embedding_dim, encoding_dim, bidirectional=True, batch_first=True)
        self.query_encoding = nn.GRU(embedding_dim, encoding_dim, bidirectional=True, batch_first=True)
        self.softmax = nn.Softmax(dim=1)


    def forward(self, document_batch, query_batch, query_lengths, mask):
        document_embedded = self.embedding_layer(document_batch)
        query_embedded = self.embedding_layer(query_batch)
        query_packed = pack_padded_sequence(query_embedded, query_lengths, batch_first = True)

        document_encoded = self.document_encoding(document_embedded)[0]
        query_encoded = self.query_encoding(query_packed)[1].view(-1, self.encoding_dim * 2, 1)

        # print(document_encoded)
        scores = torch.bmm(document_encoded, query_encoded) * mask
        probs = self.softmax(scores)
        return probs

    def loss(self, probs, answer_mask):
        answer_probs = torch.sum(probs * answer_mask, 1)
        loss_vector = -torch.log(answer_probs)
        return torch.sum(loss_vector)
        
        

