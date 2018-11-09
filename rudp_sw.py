'''*********************************************************************************
  rudp_sw SOURCE FILE - Nischith Nanjundaswamy (nischith.cnn@gmail.com)
  CREATED: 09/22/2018
  This code provides Server and Client socket functionality with TCP and UDP
  This code provides implementation for alternating bit, stop-and-wait protocol
*************************************************************************************'''

#importing the modules
import socket
import logging as log
import sys
import time

message = {"HELLO":"hello", "WORLD":"world","GOODBYE":"goodbye",
           "FAREWELL":"farewell","EXIT":"exit","OK":"ok"}
HOST_IP = '10.10.2.10'
TIMER = 100

# tcp server socket function
# accepts port as the argument
def tcp_server_socket(port):
    try:
        # create server socket
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        log.info("TCP socket created successfuly")
        server.bind((HOST_IP, port))
        server.listen(1)
        a=True
        b=1

        # accept the client connection
        while b==1:
            client, addr = server.accept()
            print("Connected with Client : ",  str(addr))

            # receive data from the client and send reply
            while a:
                data = client.recv(255)
                rec_str = data.decode('utf-8')
                print("Message from client> ",rec_str)

                if rec_str == message.get("HELLO"):
                    client.sendall(message.get("WORLD").encode('utf-8'))
                    print("Send reply >> ",message.get("WORLD"))
                elif rec_str == message.get("GOODBYE"):
                     client.sendall(message.get("FAREWELL").encode("utf-8"))
                     print("Send reply >> ",message.get("FAREWELL"))
                     log.info("Terminating Client socket connection ")
                     client.close()
                     break
                elif rec_str == message.get("EXIT"):
                     client.sendall(message.get("OK").encode("utf-8"))
                     print("Send reply >> ", message.get("OK"))
                     a = False
                     b = 2
                     client.close()
                     log.info("Terminating Client socket connection")
                     log.info("Terminating server socket connection")
                else:
                     client.sendall(rec_str.encode("utf-8"))
                     print("Send reply >> ", rec_str)

    except Exception as err:
        log.info(err)

# tcp client socket function
# accepts host and port as the argument
def tcp_client_socket(host,port):
     # create client socket and connect to server and it's port
      client = socket.socket()
      log.info("TCP socket created successfuly")
      client.connect((HOST_IP,port))
      send_str = input("Send >>")

      # send and receive data from  server
      while True:
           client.send(send_str.encode("utf-8"))
           data = client.recv(255)
           srv_msg = data.decode("utf-8")
           print("Message from server ->  ",srv_msg)

           if srv_msg == message.get("FAREWELL"):
               log.info("Closing the client connection")
               break
           elif srv_msg == message.get("OK"):
               log.info("Closing the client connection")
               break
           send_str = input("Send >>")

# udp server socket function
# accepts port as teh argument
def udp_server_socket(port,f):
    try:
        # Create server socket and bind to host and port
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        log.info("UDP socket created successfuly \n")
        server.bind((HOST_IP, port))

        list={}
        temp = None
        # Receive data frome client and send reply
        while True:
            data, addr = server.recvfrom(2000)
            print("connectd to client ", addr, "\n")

            rec_str = data.decode('utf-8','ignore')

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
                 print("Received Sequence number:- ",list[0] )
                 print("Message lenght:- ",list[1])
                 msg_write = list[2]
                 ACK = list[0]

                 if list[0] == '0' and temp!= list[0]:
                    server.sendto(('0').encode("utf-8"),addr)
                    print("sending ACK-0 to client")
                    f.write(msg_write.encode('utf-8'))
                 elif list[0] == '0' and temp == list[0]:
                     server.sendto(('0').encode("utf-8"), addr)
                     print("Duplicate packet received. Discard the packet and send ack")
                     print("Sending ACK-0 to client")
                 elif list[0] == '1' and temp!= list[0]:
                         server.sendto(('1').encode("utf-8"), addr)
                         print("sending ACK-1 to client")
                         f.write(msg_write.encode('utf-8'))
                 else:
                     server.sendto(('1').encode("utf-8"), addr)
                     print("Duplicate packet received. Discard the packet and send ack")
                     print("sending ACK-1 to client")
                 temp = ACK

    except Exception as err:
           log.info(err)

# function to receive acknowledgement.
# accepts message sent time and client socket as parameters
def wait_for_ACK(client,msg_sent_time):
    current_time = int(round(time.time() * 1000))
    time_passed = current_time - msg_sent_time

    while(time_passed < TIMER):
        client.setblocking(False)
        try:
           data = client.recv(2000)
           print("Data in Client socket =  ",data)
           if data != None:
               return data
        except socket.error:
           pass
        current_time = int(round(time.time() * 1000))
        time_passed = current_time - msg_sent_time
    return None

# udp client socket function
# accepts port as teh argument
# send packets with sequence number 0 or 1 and start timer.
# default value of timer is set to 100 milliseconds
def udp_client_socket(port,f):
    try:
       seq_number = 0
       msg_length = 0

       # create a client socket
       client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
       log.info("UDP socket created successfully")

       # Read line of data from the file and send it to server.
       # seq_number is the sequence number 0/1
       # msg_length is the length of message
       for line in f:
               msg = line.decode('utf-8','ignore')
               msg_length = len(line)
               header = str(seq_number) +'&&'+str(msg_length)
               rudp_msg = header +'&&'+ msg
               print("Sending Rudp message with seq_number:- ", seq_number)
               client.sendto(rudp_msg.encode('utf-8'), (HOST_IP, port))
               msg_sent_time = int(round(time.time() * 1000))

               ack_received = None
               ack_received = wait_for_ACK(client, msg_sent_time)

               while ack_received == None:
                   print("Did not recevice ACK from Server. "
                         "Resending the data with seq_number:- ", seq_number )
                   client.sendto(rudp_msg.encode('utf-8'), (HOST_IP, port))

                   msg_sent_time = int(round(time.time() * 1000))
                   ack_received = wait_for_ACK(client, msg_sent_time)

               while ack_received.decode('utf-8') != str(seq_number):
                   print("Received acknowledgement ACK:- ",ack_received.decode('utf-8'),
                         "is not matching seq_number:- ", seq_number,'\n')
                   print("Duplicate ACK received.Discarding the ACK and "
                         "Resending the data and wait Untill proper "
                         "ACK received for data with Seq number ",str(seq_number))
                   client.sendto(rudp_msg.encode('utf-8'), (HOST_IP, port))
                   msg_sent_time = int(round(time.time() * 1000))
                   ack_received = wait_for_ACK(client, msg_sent_time)

               if ack_received.decode('utf-8') == str(seq_number):
                       print("Received acknowledgement ACK:- ", ack_received,
                         "is matching seq_number:- ", seq_number)

               if ack_received.decode('utf-8') == str(0):
                   seq_number = 1
               else:
                   seq_number = 0

       # send and receive data from server
       print("Enter goodbye to exit client")
       send_str = raw_input("Send >>")
       while True:
           client.sendto(send_str.encode("utf-8"), (HOST_IP, port))
           data3, addr = client.recvfrom(255)
           rcv_msg2 = data3.decode("utf-8")
           print("Message from Server: ",rcv_msg2)

           if rcv_msg2 == message.get("OK"):
              break

           if rcv_msg2 == message.get("FAREWELL"):
              log.info("Closing the client connection")
              client.close()
              break

           send_str = input("Send >>")
    except Exception as err:
       log.info(err)
