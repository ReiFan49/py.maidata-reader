import dataclasses
import re
import struct

MASKED_CHARS = ('&', '+', '%', chr(92))
MASKED_TUPLES = [
  (chr(92) + k, struct.pack('=bH', 27, 257 + i))
  for i, k in enumerate(MASKED_CHARS)
]

def _left_mask(match):
  '''
  Obtain masked string from given escaped character.

  This is provided to allow easy escaping on older simai editions.
  '''
  _map = {k: v for k, v in MASKED_TUPLES}
  return _map[match.group(0)]

def _right_mask(match):
  '''
  Retrieves actual escaped character from given masked string.

  Inverse operation of _left_mask.
  '''
  _map = {v: k for k, v in MASKED_TUPLES}
  return _map[match.group(0)]

class File:
  '''
  Representation of Simai File data.
  '''

  def __init__(self, entries: dict):
    self.entries = {k: Content(k, v) for k, v in entries.items()}

  def difficulty(self, diff_id : int):
    '''
    Retrieves `lv` key of a `diff_id`.
    '''
    return self.entries.get(f'lv_{diff_id}', None)

  @property
  def difficulties(self):
    '''
    Retrieves available chart difficulties with content inside.
    '''
    return frozenset(sorted(
      int(k[6:], 10)
      for k in self.entries
      if k[:6] == 'inote_'
    ))

  @property
  def charts(self):
    '''
    Retrieves each chart contents.
    '''
    return {
      diff_id: self.entries.get(f'inote_{diff_id}')
      for diff_id in self.difficulties
    }

  @classmethod
  def parse(cls, raw : str):
    '''
    Loads a simai content given a raw string from.
    '''
    entries = {
      match.group(1): re.sub(
        r'\\e.{2}',
        _right_mask,
        match.group(2),
        flags=re.S | re.U,
      ).strip()

      for match in re.finditer(
        r'\&([a-z]+(?:_[1-9]\d*)?)=((?:(?!&\w+).)*)',
        re.sub(r'\[&+%\]', _left_mask, raw),
        flags=re.S,
      )
    }

    return cls(entries)

@dataclasses.dataclass
class Content:
  '''
  Simple struct that provides the detail of key and value of a pair.

  Supports quick conversion into simai format pair.
  '''

  key: str
  data: str

  def __str__(self):
    '''converts to simai entry pair.'''
    return '&{0}={1}'.format(self.key, self.data)

__all__ = [
  'File',
  'Content',
]
