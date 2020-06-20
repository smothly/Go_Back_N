from socket import *
import hashlib
import pickle
import random 

# 서버 소켓 설정
serverPort = 12000
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('localhost', serverPort))
serverSocket.settimeout(60)

# 신뢰성 없는 전송: 랜덤 함수를 이용하여 구현
# sender와의 차이점은 sender는 윈도우에 packet을 가지고 있을 수 있지만
# reciever는 window가 없어 성공여부를 직접 리턴하는 식으로 구현
def udt_send(packet, socket, addr):
    temp = pickle.loads(packet)
    if random.randint(0, 10) > 0: # 이 부분은 랜덤으로 unreliable한 것을 만들기 위함 10퍼센트 확룰
        socket.sendto(packet, addr)
        print('패킷 보냈습니다 ACK:', temp[0])
        return True
    else:
        print('!!!!!!!!! reciever ACK {} Loss !!!!!!!!!!'.format(temp[0]))
        return False

# checksum 확인
def not_corrupt(rcvpkt):
    if hashlib.md5(pickle.dumps([rcvpkt[0], rcvpkt[1]])).digest() == rcvpkt[2]:
        return True
    else:
        return False

# 기대하는 seqnum하고 같은지 확인
def hasSeqnum(rcvpkt, expectedSeqnum):
    if rcvpkt[0] == expectedSeqnum:
        return True
    else:
        return False

# extract: 파일 -> 리스트
def extract(packet):
    return pickle.loads(packet)

# 패킷만들기: sender와 차이점은 데이터가 포함되지 않는다는 점이다.
def make_pkt(seq_num):
    # hashlib을 활용한 체크섬 만들기
    checksum = hashlib.md5(pickle.dumps(seq_num)).digest()
    return pickle.dumps([seq_num, checksum])

print('서버: 메시지 받을 준비 완료.....')

# 초기 설정
expectedSeqnum = 0
sndpkt = make_pkt(expectedSeqnum)

while True:
    try:
        packet, clientAddress = serverSocket.recvfrom(2048)
        rcvpkt = pickle.loads(packet)
        print('sender로부터', rcvpkt[0], '패킷 받음')
        # checksum이 잘못되지 않으면
        if not_corrupt(rcvpkt):
            # seqnum 패킷 순서에 맞으면
            if hasSeqnum(rcvpkt, expectedSeqnum):
                print('체크섬과 순서 맞음 O')
                sndpkt = make_pkt(expectedSeqnum)
                # 정상적으로 보냈으면
                if udt_send(sndpkt, serverSocket, clientAddress):
                    print('순서 맞는 ACK 정상 전송', expectedSeqnum)
                    expectedSeqnum += 1
            # 순서에 맞지 않으면
            else:
                print('순서 맞지 않음 X')
                sndpkt = make_pkt(expectedSeqnum - 1) # 이전 ack를 보내서 무시하게 만듬
                udt_send(sndpkt, serverSocket, clientAddress)
                print("기대되는 Seqnum:", expectedSeqnum) # sender측에 기대되는 seqnum알려줌
        # corrupt 잘못된 패킷이면
        else:
            print('잘못된 패킷이다!')
    
    except Exception as e:
        print('서버 지속시간이 끝났습니다!')
        break
    print('=' * 20)

serverSocket.close()