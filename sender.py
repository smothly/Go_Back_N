'''
20142772 최승호
Go-Back-N
코드 윗부분은 함수 구현들이고 밑에 while문 부터 로직 시작입니다.
최대한 fsm의 함수와 동일하게 만들었습니다.
랜덤으로 Packet Loss가 발생하게 하였습니다.
'''

import os
from socket import *
import time
import hashlib
import pickle
import random

# 신뢰성 없는 전송: 랜덤 함수를 이용하여 구현
def udt_send(packet, socket, addr):
    
    temp = pickle.loads(packet)
    if random.randint(0, 10) > 0: # 이 부분은 랜덤으로 unreliable한 것을 만들기 위함
        socket.sendto(packet, addr)
        print('패킷 보냈습니다 seqnum: ', temp[0])
    else: # 10퍼센트의 확률
        print('!!!!!!!!! sender 패킷 {} Loss !!!!!!!!!!'.format(temp[0]))

# packet 만드는 함수
def make_pkt(seq_num, data):
    checksum = hashlib.md5(pickle.dumps([seq_num, data])).digest() # hashlib을 활용한 checksum 만들기
    return pickle.dumps([seq_num, data, checksum]) # pickle 라이브러리를 통하여 byte로 encoding

# checksum과 ack 확인하는 함수
def not_corrupt(rcvpkt):
    if hashlib.md5(pickle.dumps(rcvpkt[0])).digest() == rcvpkt[1]:
        # base와 ack과 같은지도 확인해야함
        if base == rcvpkt[0]:
            return True
        else:
            return False
    else:
        return False

# timer 관련 함수들
def start_timer():
    timer = time.time()
def stop_timer():
    timer = 0

# rcvpkt의 acknum 반환
def getacknum(rcvpkt):
    return rcvpkt[0]

timer = time.time() # 초기값 마지막으로 ack를 받은 시간이 저장될 예정
timeout = 7 # 타임 아웃7초로 설정

serverName = "127.0.0.1"
serverPort = 12000

# 클라이언트 소켓 생성
clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.settimeout(2) # 자동종료타임

 
# 초기 설정
filename = 'index.html'
base = 0 # window의 왼쪽
nextSeqnum = 0 # 다음으로 기대되는 seqnum
windowSize = 3 # 3으로 설정
window = [] # window 생성


# 파일로 데이터 보내기
f = open(filename, 'rb')
print('보낼 데이터 사이즈는', os.path.getsize(filename)) # 351bytes 30bytes씩 전송하므로 0 ~ 11ack를 받아야한다.
data = f.read(30)
EOF = False # 파일이 끝났는지 확인하는 변수

# 파일전송이 끝나거나 윈도우에 있는 파일 전부 ack를 받을때까지
while not EOF or window:
    # 윈도우가 꽉차지 않았으면 보내기
    if nextSeqnum < base + windowSize and not EOF:

        # 패킷 생성
        sndpkt = make_pkt(nextSeqnum, data)
        # packet을 윈도우에 넣어주기
        window.append(sndpkt)

        # 패킷 보내기
        udt_send(sndpkt, clientSocket, (serverName, serverPort))
        
        if base == nextSeqnum:
            print('타이머 시작')
            start_timer()

        nextSeqnum += 1
        data = f.read(30)

        # 데이터가 없으면 플래그 변경
        if not data:
            print('데이터 전송 완료')
            EOF = True        

    # 리시브 하는 부분
    # - try except문을 통하여 일정시간내(위의 settimeout) 응답을 받지못하면 에러부분으로 감
    try:
        packet, serverAddress = clientSocket.recvfrom(1024)
        rcvpkt = pickle.loads(packet)

        # rdt_rcv & not corrupt
        # checksum + ack 확인과정
        if not_corrupt(rcvpkt): 
            print('정상적으로', rcvpkt[0], '에 대한 Ack 받음!')
            # ack 정상적으로 받으면 window에서 삭제
            del window[0] 
            base = getacknum(rcvpkt) + 1
            if base == nextSeqnum:
                stop_timer()
            else:
                start_timer()
            
            
        # rdt_rcv & corrupt
        # seqnum이 잘못되는 경우도 포함
        else:
            print('ACK 무시: Checksum이 잘못되거나 Seqnum이 잘못됨')

    except Exception as e:
        # 타임아웃 timeout
        if time.time() - timer > timeout:
            print('타임아웃입니다.', base, '부터', nextSeqnum-1, '까지 다시 보냅니다.')
            # timer 시작하고 base~nextSeqnum - 1까지 다시보내는 과정 
            start_timer()
            for sndpkt in window:
                print(pickle.loads(sndpkt)[0], '다시 보냅니다.')
                udt_send (sndpkt, clientSocket, (serverName, serverPort))
    print('=' * 20)

f.close()
clientSocket.close()

'''
확인한 테스트들
1. 정상적으로 loss없이 가는경우 O
2. 중간에 loss가 나서 timeout이 생겨 window에 있는 것들 다시 보내기 O
3. 체크섬이 잘못되거나 ack나 seqnum이 잘못 전송되는경우 O
4. 서버측 클라이언트측 두 부분에서 unreliable send로 loss가 일어나는 경우 O
-> 결국 전부 sender측에서 ack를 제대로 받았는지만 잘 판단하면 된다.
'''