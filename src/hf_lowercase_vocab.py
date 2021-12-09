import json
import os.path as osp

from collections import OrderedDict
from transformers import AutoModel, AutoTokenizer


def hf_lowercase_vocab(tokenizer, keynet, uncased_vocab_dir='./uncased/'):

  # load original vocab
  tokenizer.save_pretrained(uncased_vocab_dir)
  json_file = json.loads(open(osp.join(uncased_vocab_dir, 'tokenizer.json')).read())
  token2id_dict = json_file['model']['vocab'] # 32500

  # lowercasing
  lower2ref_dict = {} # {'aa': [('AA', 00), ('Aa', 01), ('aa', 02)], ...}
  special_tokens = tokenizer.all_special_tokens + tokenizer.additional_special_tokens # 7
  for k, v in token2id_dict.items():
    if k in special_tokens:
      lower2ref_dict[k] = [(k, v)]
    elif k not in special_tokens:
      lower2ref_dict.setdefault(k.lower(), [])
      lower2ref_dict[k.lower()].append((k, v))
  lower2id_dict = {k: min([ref[1] for ref in v]) for k, v in lower2ref_dict.items()}

  # rearrange indices of vocab and embeddings
  lower2id_dict = OrderedDict(sorted(lower2id_dict.items(), key=lambda item: item[1]))
  for i, (k, v) in enumerate(lower2id_dict.items()): # 32164
    assert i <= v
    lower2id_dict[k] = i
    lower_emb = keynet.embeddings.word_embeddings.weight[v]
    lower_emb = lower_emb.detach().requires_grad_() # to make it a leaf embedding (new_token_emb.is_leaf == True)
    keynet.embeddings.word_embeddings.weight[i].data.copy_(lower_emb)

  # resize
  keynet.resize_token_embeddings(len(tokenizer))

  # save lowercased vocab
  json_file['model']['vocab'] = lower2id_dict
  with open(osp.join(uncased_vocab_dir, 'tokenizer.json'), 'w') as f:
    json.dump(json_file, f)

  # save vocab.txt (just for users' readability)
  with open(osp.join(uncased_vocab_dir, 'vocab.txt'), 'w') as f:
    f.write('\n'.join(list(lower2id_dict.keys())))

  # reload the saved lowercased vocab
  tokenizer = AutoTokenizer.from_pretrained(uncased_vocab_dir)

  return tokenizer, keynet
  
  
# Usage
if __name__ == '__main__':
  model = AutoModel.from_pretrained('monologg/kobigbird-bert-base') # BigBirdModel
  tokenizer = AutoTokenizer.from_pretrained('monologg/kobigbird-bert-base') # BertTokenizer
  tokenizer, model = hf_lowercase_vocab(tokenizer, model) # transformers==4.12.5
