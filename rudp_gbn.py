'''*********************************************************************************
  rudp_gbn SOURCE FILE - Nischith Nanjundaswamy (nischith.cnn@gmail.com)
  CREATED: 10/18/2018
  This code provides Server and Client socket functionality with UDP protocol
  This code provides implementation for RUDP go-back-N protocol and Congestion control
*************************************************************************************'''

#importing the modules
import socket
import logging as log
import sys
import time
import threading

message = {"HELLO":"hello", "WORLD":"world","GOODBYE":"goodbye",
           "FAREWELL":"farewell","EXIT":"exit","OK":"ok"}
HOST_IP = '10.10.2.10'
send_seq_num = 0
recv_seq_num = None
ack_num = None
msg_sent_time = None
cwnd = 4

# udp server socket function
# accepts port as teh argument
def udp_server_socket(port,f):
    try:
        # Create server socket and bind to host and port
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        log.info("UDP socket created successfuly")
        server.bind((HOST_IP, port))

        # Receive data frome client and send reply
        while True:
            data, addr = server.recvfrom(5000)
            print("connectd to client ", addr)
            rec_str = data.decode('utf-8')

            if rec_str == message.get("HELLO"):
                server.sendto(message.get("WORLD").encode('utf-8'), addr)
                print("Message from client: ", rec_str)
                print("Send reply >> ", message.get("WORLD"))
                f.close()
            elif rec_str == message.get("GOODBYE"):
                server.sendto(message.get("FAREWELL").encode("utf-8"), addr)
                print("Message from client: ",rec_str)
                print("Send reply >> ", message.get("FAREWELL"))
                f.close()
                #time.sleep(2)
                break
            elif rec_str == message.get("EXIT"):
                server.sendto(message.get("OK").encode("utf-8"), addr)
                print("Message from client: ", rec_str)
                print("Send reply >> ", message.get("OK"))
                log.info("Terminating server socket connection")
                f.close()
                server.close()
            else:
                list = rec_str.split('&&')
                print("Received Sequence number:- ", list[0])
                print("Message lenght:- ", list[1])
                msg_write = list[2]
                print ("encoding:132")

                ACK = list[0]

                if list[0] == '0':
                    print("encoding:138")
                    server.sendto(('0').encode("utf-8"), addr)
                    print("sending ACK-0 to client")
                    f.write(msg_write.encode('utf-8'))
                    temp = list[0]
                elif (int(temp) + 1) == int(ACK):
                    print("encoding:143")
                    server.sendto(ACK.encode("utf-8"), addr)
                    print("sending ACK-", ACK.encode("utf-8"), "to client")
                    f.write(msg_write.encode('utf-8'))
                    temp = int(ACK)
                else:
                    print("encoding:148")
                    server.sendto(str(temp).encode(("utf-8")), addr)
                    print("Received packet with sequence number",ACK ,"is not in order")
                    print("Did not receive packet with seq nuber",(int(temp) + 1),
                          "sending ACK-",temp ,"to client")

    except Exception as err:
        log.info(err)

# function to send data packets.
# accept client socket, port, actual data from file and sequence number
def send_msg(msg, send_seq_num, client, port):
    msg_length = len(msg)
    header = str(send_seq_num) + '&&' + str(msg_length)
    rudp_msg = header + '&&' + msg
    print("Sending Rudp message with seq_number:- ",send_seq_num, "\n")
    client.sendto(rudp_msg.encode('utf-8'), (HOST_IP, port))

# function to send data packets.
# delay introduced by default is 75 millisecond at line #185.
# default port is 2196.
# congestion window cwnd is set to 4 and doubles every time.
# when there is a packet loss congestion window is reduced to half.
def send_thread(client,length,lines,port):
    global send_seq_num, recv_seq_num, msg_sent_time, cwnd
    while send_seq_num < length:
        flag = True
        if cwnd == 0:
            cwnd = 1
        for i in range(cwnd):
            if send_seq_num + i < length:
                send_msg(lines[send_seq_num + i], send_seq_num + i, client, port)
                if i == 0:
                    msg_sent_time = int(round(time.time() * 1000))
            else:
                send_seq_num = length
                sys.exit();
                break
        while (msg_sent_time + 75) > int(round(time.time() * 1000)):
            if recv_seq_num == (send_seq_num + cwnd):
                flag = False
                cwnd *= 2
                break
            continue
        if flag:
            cwnd /= 2
        send_seq_num = recv_seq_num
    sys.exit();

# function to receive acknowledgements
# accepts length(number of lines) of the data and client socket
def ack_thread(client,length):
    global recv_seq_num, msg_sent_time, send_seq_num
    ack_num = None
    recv_seq_num = 0

    while recv_seq_num < length:
        client.setblocking(False)
        try:
            ack_num = client.recv(2000)
            print("Received ACK from Server",ack_num)
        except socket.error:
            pass
        if ack_num == None:
            ack_num = '-1'
        if int(ack_num) == recv_seq_num:
            recv_seq_num = recv_seq_num + 1
            print("recv_seq_num: ", recv_seq_num)
            msg_sent_time = int(round(time.time() * 1000))
    sys.exit();


# udp client socket function
# accepts port as the argument
def udp_client_socket(port,f):
    # create a client socket
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    log.info("UDP socket created successfully")
    msg_length = 0
    lines = []

    for line in f:
        lines.append(line.decode('utf-8', 'ignore'))
    length = len(lines)

    thread1 = None
    thread2 = None
    print("Creating thread1 and thread2 for "
          "sending data packets and receiving acknowldgements")
    try:
        thread1 = threading.Thread(target=send_thread, args=(client,length,lines,port))
        thread1.start()
    except:
        print("Closing  connection")
    try:
        thread2 = threading.Thread(target=ack_thread, args=(client,length))
        thread2.start()
    except:
        print("Closing  connection")

    thread1.join()
    thread2.join()
    print ("Exited both the threads")

    while True:
        try:
            print("Receive msg from server")
            data, addr = client.recvfrom(255)
        except socket.error:
            break
        rcv_msg = data.decode("utf-8")
        if rcv_msg == None:
            break
    print("Enter goodbye to exit client")
    send_str = raw_input("Send >>")

    while True:
        client.sendto(send_str.encode("utf-8"), (HOST_IP, port))
        client.setblocking(True);
        try:
            data, addr = client.recvfrom(255)
        except socket.error:
            pass
        rcv_msg = data.decode("utf-8")
        print("Message from Server: ",rcv_msg)

        if rcv_msg == message.get("FAREWELL"):
           log.info("Closing the client connection")
           client.close()
           break

        send_str = raw_input("Send >>")
