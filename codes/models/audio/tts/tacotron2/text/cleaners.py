""" from https://github.com/keithito/tacotron """

'''
Cleaners are transformations that run over the input text at both training and eval time.

Cleaners can be selected by passing a comma-delimited list of cleaner names as the "cleaners"
hyperparameter. Some cleaners are English-specific. You'll typically want to use:
  1. "english_cleaners" for English text
  2. "transliteration_cleaners" for non-English text that can be transliterated to ASCII using
     the Unidecode library (https://pypi.python.org/pypi/Unidecode)
  3. "basic_cleaners" if you do not want to transliterate (in this case, you should also update
     the symbols in symbols.py to match your data).
'''

import re
from unidecode import unidecode
from .numbers import normalize_numbers


# Regular expression matching whitespace:
_whitespace_re = re.compile(r'\s+')

# List of (regular expression, replacement) pairs for abbreviations:
_abbreviations = [(re.compile('\\b%s\\.' % x[0], re.IGNORECASE), x[1]) for x in [
  ('g.', 'godina'),
  ('r.', 'razred'),
  ('t.', 'tona'),
  ('n. e.', 'nove ere'),
  ('p.n.e.', 'pre nove ere'),
  ('l. k.', 'lična karta'),
  ('br.', 'broj'),
  ('sv.', 'sveti'),
  ('str.', 'strana'),
  ('mn.', 'množina'),
  ('i dr.', 'i drugi'),
  ('i sl.', 'i slično'),
  ('ul.', 'ulica'),
  ('inž.', 'inženjer'),
  ('srp.', 'srpski'),
  ('dr', 'doktor'),
  ('mr', 'magistar'),
  ('gdin', 'gospodin'),
  ('gđa', 'gospođa'),
  ('gđica', 'gospođica'),
  ('tzv.', 'takozvani'),
  ('itd.', ' i tako dalje'),
  ('bb.', 'bez broja'),
  ('npr.', 'na primer'),
  ('V', 'volt'),
  ('W', 'vat'),
  ('J', 'džul'),
  ('A', 'amper'),
  ('T', 'tesla'),
  ('g', 'gram'),
  ('kg', 'kilogram'),
  ('l', 'litar'),
  ('m', 'metar'),
  ('km', 'kilometar'),
  ('cm', 'centimetar'),
  ('SANU', 'Srpska akademija nauka i umetnosti'),
  ('VMA', 'Vojnomedicinska akademija'),
  ('MMF', 'Međunarodni monetarni fond'),
  ('NIN', 'Nedeljne informativne novine'),
  ('AVNOJ', 'Antifašističko veće narodnog oslobođenja Jugoslavije'),
]]


def expand_abbreviations(text):
  for regex, replacement in _abbreviations:
    text = re.sub(regex, replacement, text)
  return text


def expand_numbers(text):
  return normalize_numbers(text)


def lowercase(text):
  return text.lower()


def collapse_whitespace(text):
  return re.sub(_whitespace_re, ' ', text)


def convert_to_ascii(text):
  return unidecode(text)


def basic_cleaners(text):
  '''Basic pipeline that lowercases and collapses whitespace without transliteration.'''
  text = lowercase(text)
  text = collapse_whitespace(text)
  return text


def transliteration_cleaners(text):
  '''Pipeline for non-English text that transliterates to ASCII.'''
  text = convert_to_ascii(text)
  text = lowercase(text)
  text = collapse_whitespace(text)
  return text


def english_cleaners(text):
  '''Pipeline for English text, including number and abbreviation expansion.'''
  # text = convert_to_ascii(text)
  text = lowercase(text)
  # text = expand_numbers(text)
  text = expand_abbreviations(text)
  text = collapse_whitespace(text)
  text = text.replace('"', '')
  return text
