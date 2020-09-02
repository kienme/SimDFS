# SimpDFS

> Simple Distributed File System 

A file system meant to tolerate independent node failures

## Supported operations

- Read  
- Write  

## High level design

- Data nodes = DN ; These are hosts that store data
- Some nodes (one currently) are designated as metadata nodes (MDN)
- MDNs use some policy (random, here) to decide where data blocks will be written
- Client is responsible for reading and writing all blocks/replicas
- List of MDNs can be queried from some service, say zookeeper (present in a config file currently)

### Write operation - Steps 

Client does the following -
1. Initialize list of MDNs (scope for caching; just reads config file currently)
2. Request an MDN (randomly selected) for block mapping, by sending file size as a param
3. Send blocks to hosts (sequential, currently)
4. Inform MDN about the completion status (not done)

### Read operation - Steps 

Client does the following - 
1. Initialize list of MDNs (same as step 1 of write)
2. Request for file block mapping (ask each MDN if it contains file metadata)
3. Get blocks from hosts (retry with replica; display corruption message if unable to)

## Configs 

### Client 

- MDN list  

### MDN 

- Replication factor (only used while writing, currently)  
- Block size (used only when returning mapping for a write) 
- DN list 

## Low level 

- RPC (XML+HTTP) for communication
- Three different programs (DN, MDN, Client)
- Ports: DN=1111 MDN=2222

### Block splitting and replication 

This happens in step 2 of write (get_locations_new in DN API described below)  
1. MDN receives a request for file of size F
2. MDN reads block size B and replication factor R from config  
Total number of unique blocks T is ceil(F/B)
4. Returns list of size T, each entry is a tuple described in MDN data structures section below   
Size of the [hosts] list in each entry is R 

### Block storage 

- Naming: File path (replace / with -) + random id + sequence number (No random id in this version)
- In the rare event of collision with existing block name, change random id (Not done)

### API 

#### DN 

- put_block(id, data) - Persist data block with given id to disk 
- get_block(id) - Read block with given id from disk and return 

#### MDN 

- get_locations(path) - Return list of block ids and their locations 
- get_locations_new(file_size) - Return block size and list of hosts where blocks are to be written 

### MDN data structures 

- For block locations: Map path (string) to a list of lists, where i'th element is the list of hosts where the i'th block id is stored 
- For directory listing: Map path (string) to a list of tuples [<name,d>], where name is name of files/dirs under path and d is flag indicating if it is a directory (out of scope)

## Run/Test/Deploy

Ensure docker is set up, and docker-compose is installed and run
```
docker-compose up --build --scale dn=3 -d
```
This will build the images and start up all containers. Might take some time on the first run.  


List all containers
```
docker ps -a
```

Attach to the client container to access SimpDFS
```
docker attach simpdfs_client_1
```
Use the client to put and get files
```
root@293bf4e67087:/usr/src/app# echo "This is a sample file to test SimpDFS. This is another sentence." > sample_in
root@293bf4e67087:/usr/src/app# python3 client.py put sample_in /mypath/myfile
Starting client
root@293bf4e67087:/usr/src/app# python3 client.py get /mypath/myfile sample_out
Starting client
root@293bf4e67087:/usr/src/app# cat sample_out
This is a sample file to test SimpDFS. This is another sentence.
root@293bf4e67087:/usr/src/app#
```


Stop/start containers to test node failures
