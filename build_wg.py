#!/usr/bin/python

import argparse
import os
import sys
import os.path
from colorama import Fore, Style, init
from time import sleep

# Confugre Argument Parse

wg_parser = argparse.ArgumentParser()

wg_parser.add_argument('-p', dest='port', action='store', required=True, help='Specify the port for the server')
wg_parser.add_argument('-c', '--client', dest='client', action='store_true', help='Use this to create a client config')
wg_parser.add_argument('-s', '--server', dest='server', action='store_true', help='Use this to create a client config')
wg_parser.add_argument('-i', dest='ip', action='store', required=True, help='Place the ip you want the server to use Ex: 10.0.0.1/24')
wg_parser.add_argument('-k', '--key', action='store', dest='key', help='Place the public key for the server here')
wg_parser.add_argument('-e', '--endpoint', action='store', dest='endpoint', help='Place ther server IP here')
wg_parser.add_argument('-a', '--allow', action='store', dest='allow', help='Place the allowed IPs for communiction here Ex: 10.0.0.0/24')

if len(sys.argv) == 1:
    wg_parser.print_help(sys.stderr)
    sys.exit(1)

wg = wg_parser.parse_args()

# Set colorama to reset colors after each use

init(autoreset=True)

# Delete configuration file if it already exists

wg0 = "/etc/wireguard/wg0.conf"

if os.path.isfile(wg0):
    os.remove(wg0)

# Build the correct wireguard config file

if wg.client and wg.server:
    print(Fore.RED+Style.BRIGHT+"You must select to build only a client or a server")
elif wg.client:
    if wg.key and wg.endpoint and wg.allow:
        print("")
        print(Fore.YELLOW+Style.BRIGHT+"Building Client config now")
        os.system("umask 077")
        os.system("wg genkey | tee privatekey | wg pubkey > publickey")
        os.system("echo [Interface] >> {wg0}".format(wg0=wg0))
        sleep(1)
        with open("privatekey") as p:
            priv = p.readline()
            priv = priv.strip("\n")
        p.close
        os.system("echo 'PrivateKey = {priv}' >> {wg0}".format(priv=priv, wg0=wg0))
        os.system("echo Address = {addr} >> {wg0}".format(addr=wg.ip, wg0=wg0))
        os.system("echo [Peer] >> {wg0}".format(wg0=wg0))
        os.system("echo PublicKey = {key} >> {wg0}".format(key=wg.key, wg0=wg0))
        os.system("echo Endpoint = {srv}:{port} >> {wg0}".format(srv=wg.endpoint, port=wg.port, wg0=wg0))
        os.system("echo AllowedIPs = {allow} >> {wg0}".format(allow=wg.allow, wg0=wg0))
        print(Fore.GREEN+"Server config complete")
    else:
        print(Fore.RED+Style.BRIGHT+"Building a client config file requires a -k <public key>, -e <server ip>, and -a <allowed IPS>")
elif wg.server:
    print("")
    print(Fore.YELLOW+Style.BRIGHT+"Building Server config now")
    os.system("umask 077")
    os.system("wg genkey | tee privatekey | wg pubkey > publickey")
    os.system("echo [Interface] >> {wg0}".format(wg0=wg0))
    sleep(1)
    with open("privatekey") as p:
        priv = p.readline()
        priv = priv.strip("\n")
    p.close
    os.system("echo 'PrivateKey = {priv}' >> {wg0}".format(priv=priv, wg0=wg0))
    os.system("echo Address = {addr} >> {wg0}".format(addr=wg.ip, wg0=wg0))
    os.system("echo Listenport = {port} >> {wg0}".format(port=wg.port, wg0=wg0))
    os.system("echo 'PostUp = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE; iptables -I INPUT -p tcp --dport {port} -j ACCEPT; sysctl -w net.ipv4.ip_forward=1' >> {wg0}".format(wg0=wg0, port=wg.port))
    os.system("echo 'PostDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE; iptables -D INPUT -p tcp --dport {port} -j ACCEPT; sysctl -w net.ipv4.ip_forward=0' >> {wg0}".format(wg0=wg0, port=wg.port))
    os.system("echo SaveConfig = true >> {wg0}".format(wg0=wg0))
    print(Fore.GREEN+"Server config complete")
else:
    print("You must select either a -c for client or -s for server")
