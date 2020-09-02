from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler


# TODO: Read from config file
BLOCK_STORE_PATH = './blocks'


class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)


def get_block_name(path, seq):
    '''Return block id (name) for given file path and seq.'''
    # Replace / with - and append seq number
    # No validation done on path or block
    # Chances of colision. E.g: /a/b/c and /a/b-c both map to a-b-c
    # Also first character is always a - (because path starts with /). Meh.
    return '{}-{}'.format(path.replace('/', '-'), str(seq))


def put_block(path, seq, data):
    '''Write given data into a file named id under BLOCK_STORE_PATH.'''
    block_name = get_block_name(path, seq)
    print('Writing block ' + block_name)
    with open(BLOCK_STORE_PATH+'/'+block_name, 'w') as f:
        f.write(data)

    # Should be returning success/failure
    return 1


def get_block(path, seq):
    '''Return contents of file named id under BLOCK_STORE_PATH.'''
    block_name = get_block_name(path, seq)
    print('Fetching block ' + block_name)
    with open(BLOCK_STORE_PATH+'/'+block_name, 'r') as f:
        data = f.read()

    return data


def main():
    print('Starting DN')

    # put_block('/my/dir/file', 6, 'hello file')
    # print(get_block('/my/dir/file', 6))


    with SimpleXMLRPCServer(('0.0.0.0', 1111), requestHandler=RequestHandler) as server:
        server.register_introspection_functions()

        server.register_function(get_block)
        server.register_function(put_block)

        print('Awaiting requests')
        server.serve_forever()

    print('Stopping DN')


if __name__ == "__main__":
    main()
