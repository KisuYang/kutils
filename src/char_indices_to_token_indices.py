def char_indices_to_token_indices(self, start_char_idx:int, end_char_idx:int, offsets:List[Tuple[int]], n_texts=1):
  
  start_token_idx, end_token_idx = -100, -100
  special_token_count = 0
  
  for i, (s, t) in enumerate(offsets):
    if s == t == 0:
      special_token_count += 1
    elif special_token_count == n_texts: # after [CLS] if n_texts == 1. after [CLS] and [SEP] if n_texts == 2.
      if s <= start_char_idx:
        start_token_idx = i
      if t >= end_char_idx:
        end_token_idx = i + 1
        break
  
  if end_token_idx == -100:
    start_token_idx = -100

  return start_token_idx, end_token_idx
