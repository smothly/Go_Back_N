num = 1
data = open('./index.html', 'rb')
f = data.read(20)

import hashlib
import pickle
import time
sndpkt = []
sndpkt.append(1)
sndpkt.append(f)
# h = hashlib.md5()
# h.update(pickle.dumps(sndpkt))
# a = pickle.dumps(sndpkt)
# print(a)
# print(type(a))
# print(pickle.loads(a))
# sndpkt.append(h.digest())
# print(h.digest())
# hashlib.md5(pickle.dumps(sndpkt)).digest()
# print(sndpkt)


a = time.time()

print(time.time() -  a)