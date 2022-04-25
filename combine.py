from operator import contains
import zipfile
import os
from pathlib import Path
import sys
import argparse
import shutil

OUTPUT_FILE = 'openvpn.ovpn'
OPENVPN_FILE = 'openvpn.ovpn'
CA_FILE = 'ca.crt'
CLIENT_FILE = 'client.crt'
CLIENTKEY_FILE = 'client.key'

def unpackZip(zipPath, unpackDirectory = None):
    if unpackDirectory == None:
        unpackDirectory = Path(zipPath).parent.absolute()
    with zipfile.ZipFile(zipPath, 'r') as zip_ref:
        zip_ref.extractall(unpackDirectory)
    return unpackDirectory

def main():
    parser = argparse.ArgumentParser(description='Combine several OpenVPN files into one config file')
    parser.add_argument('-s','--server', metavar='SERVER', dest='server', help='Server address')
    parser.add_argument('-n','--name', metavar='NAME', dest='name', help='User name')
    parser.add_argument('-p','--password', metavar='PASSWORD', dest='password', help='Password')
    parser.add_argument('zip_path', metavar='PATH', help='Path to zip archive')
    args = parser.parse_args()
    # work with command line. 
    # 1 argument and path to zip file - unpack, and combine
    # 1 argument, path to connection files - combine
    if args.name == None or args.password == None: raise(argparse.ArgumentError)

    path = args.zip_path
    unpackDirectory = args.zip_path
    unpacked = False
    if os.path.isfile(path) and path.endswith('.zip'): # zip archive
        unpackDirectory = unpackZip(path, os.path.join(os.getcwd(), 'temp'))
        unpacked = True
    elif os.path.isdir(unpackDirectory):
        pass
    else:
        print('Cannot recognize input')
        raise(FileNotFoundError)
    if not set([CA_FILE, CLIENT_FILE, CLIENTKEY_FILE, OPENVPN_FILE]).issubset(set(os.listdir(unpackDirectory))): # check existance of all necesarly file
        print('Cannot recognize input')
        raise(FileNotFoundError)

    with open(OUTPUT_FILE, 'w') as out_f:
        # add common file
        with open(os.path.join(unpackDirectory, OPENVPN_FILE), 'r') as openvpn_file:
            for row in openvpn_file.readlines():
                for ext in ['auth-user-pass','ca ca.crt','cert client.crt','key client.key']:
                    if (ext in row) or (row == '\n'): break
                else:
                    out_f.write(row.replace('\n', '')+'\n')
        
        # add user/password
        out_f.write('<auth-user-pass>\n')
        out_f.write(str(args.name)+'\n')
        out_f.write(str(args.password)+'\n')
        out_f.write('</auth-user-pass>\n')

        # add ca
        out_f.write('<ca>\n')
        with open(os.path.join(unpackDirectory, CA_FILE), 'r') as ca_file:
            out_f.write(''.join([x for x in ca_file.readlines()]))
        out_f.write('</ca>\n')

        # add client
        out_f.write('<cert>\n')
        with open(os.path.join(unpackDirectory, CLIENT_FILE), 'r') as client_file:
            out_f.write(''.join([x for x in client_file.readlines()]))
        out_f.write('</cert>\n')

        # add key
        out_f.write('<key>\n')
        with open(os.path.join(unpackDirectory, CLIENTKEY_FILE), 'r') as key_file:
            out_f.write(''.join([x for x in key_file.readlines()]))
        out_f.write('</key>\n')
    
    # remove temp dir
    if unpacked:
        shutil.rmtree(unpackDirectory)

if __name__ == '__main__':
    main()