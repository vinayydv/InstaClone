from paralleldots import set_api_key, get_api_key
from paralleldots import similarity,emotion, sentiment
import json

set_api_key("rpMuzF79DEc91DyPeTe3Dgs1EZ3CYjDC2YRxRGyQQoo")
a = 'bad'
r = sentiment('bad ')
print type(r)
print r
print r['sentiment']


