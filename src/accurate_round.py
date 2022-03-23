from typing import Union


def accurate_round(x:Union[int, float], ndigits:int=None):
  a = -x if x < 0 else x # absolute
  i = 0 if ndigits is None else ndigits
  A = a * 10 ** i
  A = int(A) if A - int(A) < 0.5 else int(A) + 1 # round
  a = A / 10 ** i
  y = -a if x < 0 else a
  if type(x) is int or ndigits is None: # the same as built-in round()
    y = int(y)
  return y
  

if __name__ == '__main__':
  assert accurate_round(2.5) == 3 # built-in round(2.5) returns 2
  assert accurate_round(3.5) == 4 # built-in round(3.5) returns 4
