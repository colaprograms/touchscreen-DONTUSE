import urllib, urllib.request
import random
from bs4 import BeautifulSoup

RN_LOW = 1000001
RN_HIGH = 3835994
def randomurl():
  URL = "https://mercury.concordia.ca/search/?searchtype=.&searcharg=b%07d"
  return URL % random.randint(RN_LOW, RN_HIGH)

def getrec():
  try:
    req = urllib.request.urlopen( randomurl() )
  except urllib.error.HTTPError as e:
    return {
      'code': e.code,
      'reason': e.reason,
      'headers': e.headers
    }
  soup = BeautifulSoup(req.read(), 'html.parser')
  return {
    'code': req.getcode(),
    'soup': soup
  }
