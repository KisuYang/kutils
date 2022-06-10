from os import cpu_count
from copy import deepcopy
from parmap import starmap
from tqdm.auto import tqdm
from typing import Set, List, Tuple, Union
from datasketch import MinHash, MinHashLSH


def shingling(text:str, k:int=10) -> Set[str]:
  return set([text[i:i+k] for i in range(len(text) - k + 1)])

def jaccard_similarity(set1:Set, set2:Set) -> float:
  return len(set1 & set2) / len(set1 | set2)

def create_signature(document:str, key:Union[int, str], minhash:MinHash):
  minhash.update_batch([shingle.encode("utf-8") for shingle in shingling(document)])
  return (key, minhash)

def find_similar_pairs(documents:List[str], num_perm=256, threshold=0.7) -> List[Tuple[str, str]]:

  # create signatures
  minhash = MinHash(num_perm=num_perm, seed=0)
  signatures = starmap(
      create_signature,
      [(doc, i_doc, deepcopy(minhash)) for i_doc, doc in enumerate(documents)],
      pm_processes=cpu_count(),
      pm_pbar=True)

  # create LSH
  lsh = MinHashLSH(threshold=threshold, num_perm=num_perm)
  for (key, minhash) in tqdm(signatures, desc="insert"):
    lsh.insert(key, minhash)

  # search
  similar_pairs = []
  for (key, minhash) in tqdm(signatures, desc="search"):
    sim_keys = lsh.query(minhash)
    if len(sim_keys) > 1:
      sim_keys.remove(key)
      similar_pairs.extend([(key, sim_key) for sim_key in sim_keys if key < sim_key])

  return similar_pairs

def deduplicate_txt_file(txt_path:str, new_path:str=None, **kwargs):

  if new_path is None:
    new_path = txt_path + ".deduplicated"
  
  with open(txt_path, "r", encoding="utf-8") as f:
    lines = [line.strip() for line in f.readlines()]
  
  keeping_indices = list(range(len(lines)))
  similar_pairs = find_similar_pairs(lines, **kwargs)
  for (doc_idx1, doc_idx2) in similar_pairs:
    if (doc_idx1 in keeping_indices) and (doc_idx2 in keeping_indices):
      if len(lines[doc_idx1]) > len(lines[doc_idx2]):
        keeping_indices.remove(doc_idx2)
      else:
        keeping_indices.remove(doc_idx1)

  print(f"Drop {len(lines) - len(keeping_indices)} duplicates.")
  print(f"Please wait until new .txt file has been completely written.")
  with open(new_path, "w", encoding="utf-8") as f:
    for doc_idx in keeping_indices:
      f.write(lines[doc_idx] + "\n")


if __name__ == "__main__":
  deduplicate_txt_file("./data/corpus/kowiki.txt", num_perm=256, threshold=0.7)
