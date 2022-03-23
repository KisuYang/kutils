def hf_add_tokens(tokenizer, model, tokens:List[str]):
  tokenizer.add_tokens(new_tokens=tokens)
  model.resize_token_embeddings(len(tokenizer))
  return tokenizer, model

def hf_add_special_tokens(tokenizer, model, special_tokens:Dict[str, str]):
  # e.g., special_tokens = {'subj_token': '<subj>'}
  orig_num_tokens = len(tokenizer)
  num_added_tokens = tokenizer.add_special_tokens({'additional_special_tokens': list(special_tokens.values())})
  tokenizer.__dict__.update(special_tokens)
  if num_added_tokens > 0:
    model.resize_token_embeddings(new_num_tokens=orig_num_tokens + num_added_tokens)
  return tokenizer, model
