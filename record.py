import urllib, urllib.request
import random
from bs4 import BeautifulSoup
import json

RN_LOW = 1000001
RN_HIGH = 3835994
def randomurl():
  URL = "https://mercury.concordia.ca/search/?searchtype=.&searcharg=b%07d"
  return URL % random.randint(RN_LOW, RN_HIGH)

def remove_some_styling(tag):
  for z in tag.select("strong"):
    z.unwrap()

def one_child(entry):
  names = entry.select(".bibInfoLabel")
  count = len(names)
  if count == 0:
    return # this one is empty maybe?
  if count > 1:
    raise Exception("more than one bibInfoLabel")
  name = names[0]

def getrec():
  try:
    req = urllib.request.urlopen( randomurl() )
  except urllib.error.HTTPError as e:
    return {
      'code': e.code,
      'reason': e.reason,
      'headers': e.headers
    }
  try:
    soup = BeautifulSoup(req.read(), 'html.parser')
    fiel = {}
    for z in fiel.select(".bibInfoEntry"):
      remove_some_styling(z)
      name = get_name_from_entry(z)
      name = name.string
      datas = z.select(".bibInfoData")

  except Exception as e:
    return {
      'code': 200,
      'fields': fiel,
      'error': repr(e)
    }
  return {
    'code': req.getcode(),
    'fields': fiel,
    'error': None
  }
