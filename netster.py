'''*************************************************************
  netster SOURCE FILE - Nischith Nanjundaswamy (nischith.cnn@gmail.com)
  CREATED: 09/22/2018
  This code provides Server and Client socket functionality with Stop and wait
  Go-back-N
*************************************************************'''

import os
import time
import argparse
import socket
import logging as log

# Importing the assignment module a2.
from a2 import *

DEFAULT_PORT=2196

# This Server fucntion accepts host, protocol and port as the argument
# host is the Server IP, protocl is UDP/TCP and port is the Default port 12345'''
def run_server(host, port, protocol,f, file):
    log.info("Hello, I am a server...!!")

    if protocol is True:
        udp_server_socket(port, f)
    else:
         tcp_server_socket(port)

# This Client fucntion accepts host and port as the argument
# host is the Server IP and port is the Default port 12345'''
def run_client(host, port, protocol, f):
    log.info("Hello, I am a client...!!")

    if protocol is True:
        udp_client_socket(port,f)
    else:
         tcp_client_socket(host,port)

def main():
    parser = argparse.ArgumentParser(description="SICE Network netster")
    parser.add_argument('-p', '--port', type=str, default=DEFAULT_PORT,
                        help='listen on/connect to port <port> (default={}'
                        .format(DEFAULT_PORT))
    parser.add_argument('-i', '--iface', type=str, default='0.0.0.0',
                        help='listen on interface <dev>')
    parser.add_argument('-f', '--file', type=str,
                        help='file to read/write')
    parser.add_argument('-u', '--udp', action='store_true',
                        help='use UDP (default TCP)')
    parser.add_argument('-r', '--rudp', type=int, default=0,
                        help='use RUDP (1=stopwait, 2=gobackN)')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Produce verbose output')
    parser.add_argument('host', metavar='host', type=str, nargs='?',
                        help='connect to server at <host>')

    args = parser.parse_args()
    print(args)
    # configure logging level based on verbose arg
    level = log.DEBUG if args.verbose else log.INFO

    f = None
     # open the file if specified
    if args.file:
        try:
            mode = "rb" if args.host else "wb"
            f = open(args.file, mode)
        except Exception as e:
            print("Could not open file: {}".format(e))
            exit(1)

    # Here we determine if we are a client or a server depending
    # on the presence of a "host" argument.
    if args.host:
        log.basicConfig(format='%(levelname)s:client: %(message)s',
                        level=level)
        run_client(args.host, args.port, args.udp, f)
        print(args.udp)
    else:
        log.basicConfig(format='%(levelname)s:server: %(message)s',
                        level=level)
        run_server(args.host, args.port, args.udp, f, args.file)

if __name__ == "__main__":
    main()


