import click
import os
import sys

import xmlrpc.client


# TODO: Read from config file
MDN_LIST = ['http://simpdfs_mdn_1:2222']


@click.group()
def cli():
    pass


@cli.command()
@click.argument('path')
@click.argument('file')
def get(path, file):
    print('Starting download...')
    # Just contacting the first MDN in our list
    with xmlrpc.client.ServerProxy(MDN_LIST[0]) as mdn:
        try:
            map = mdn.get_locations(path)
        except xmlrpc.client.Fault as fault:
            print('Unable to fetch metadata. Does the file exist?')
            sys.exit(1)
        except Exception as exception:
            print('Unable to connect to MDN.')
            sys.exit(1)

    with open(file, 'w') as f:
        # Each block
        for i in range(0, len(map)):
            got_block = False
            # Each replica
            for host in map[i]:
                try:
                    with xmlrpc.client.ServerProxy(host) as dn:
                        block = dn.get_block(path, i)
                        f.write(block)
                        got_block = True
                        # Successful read, no need to retreive other replicas
                        break
                except:
                    print('Failed to read block from ' + host + '. Trying next replica.')
            # Did not get any replica for a block
            if not got_block:
                print('Unable to download file.')
                sys.exit(1)
    
    print('Download complete.')


@cli.command()
@click.argument('file')
@click.argument('path')
def put(file, path):
    print('Starting upload...')
    # Just contacting the first MDN in our list
    with xmlrpc.client.ServerProxy(MDN_LIST[0]) as mdn:
        file_size = os.path.getsize(file)   # Bytes
        try:
            map = mdn.get_locations_new(path, file_size)
        except xmlrpc.client.Fault as fault:
            print('Unable to fetch metadata. Does the file exist?')
            sys.exit(1)
        except Exception as exception:
            print('Unable to connect to MDN.')
            sys.exit(1)
    
    # Open file, and send blocks to hosts described by map
    # Scope for optimization, we might be connecting to the same host multiple times
    # Trade off b/w network connection and file access times
    # Can parallelize
    with open(file, 'r') as f:
        for i in range(0, len(map['map'])):
            # MDN gives the block size
            block = f.read(map['block_size'])
            # Send this to all replicas
            put_block = False
            for host in map['map'][i]:
                # Connect to dn
                with xmlrpc.client.ServerProxy(host) as dn:
                    # Such indentation Very complexity Wow
                    try:
                        dn.put_block(path, i, block)
                        put_block = True
                    except Exception as exception:
                        print('Unable to write to ' + host + '. Skipping.')
            if not put_block:
                print('Unable to upload. Aborting.')
                sys.exit(1)

    print('Upload complete.')
                    


def main():
    cli()


if __name__ == "__main__":
    main()
