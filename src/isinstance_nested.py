from typing import TypeVar, List, Dict


def isinstance_nested(x, typ, skim:bool=True) -> bool:
  '''
      Args:
          skim (:bool):
              Check only the first item of List or Dict

      This function supports only int, str, typing.List and typing.Dict types
      so that you can use it to check if x is List, List[int], List[List[str]], List[Dict[str, List]] etc.

      Notice that
          x=[], typ=List[int] -> True
  '''
  result = True

  if hasattr(typ, '__args__'):
    for i_arg, arg in enumerate(typ.__args__):

      if type(x) == typ.__origin__ == list:
        if len(x) == 0:
          return True
        else:
          for e in x:
            _result = isinstance_nested(e, arg, skim)
            result = result and _result
            if not result or skim:
              break

      elif type(x) == typ.__origin__ == dict:
        if len(x) == 0:
          return True
        else:
          for k, v in x.items():
            if i_arg == 0:
              _result = isinstance_nested(k, arg, skim)
              result = result and _result
            elif i_arg == 1:
              _result = isinstance_nested(v, arg, skim)
              result = result and _result
            if not result or skim:
              break

      else:
        result = False # different or unsupported types

  else:
    if hasattr(typ, '__origin__'): # if a leaf type is List or Dict which has no args
      _result = type(x) == typ.__origin__
    else: # int, str etc.
      _result = type(x) == typ
    result = result and _result

  return result


# Usage
if __name__ == '__main__':
  result = isinstance_nested([{'a': [1, 2, 3]}], List[Dict[str, List[int]]]) # True
