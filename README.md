Redis Backups Manager
=====================


Redis backups manager (horribly named) started out as a project with a very specific purpose. Basically the problem that was presented while using redis as a persistent data store (I know...Spare the arguing) was that the main method of backing up the store was to do a disk dump(bg save on timed intervals). We ran into a subset of problems with this approach, some of which could be argued as solved by using AOF though we ran into a whole different subset of problems there as well. This was the best approach at the time with what we had to work with....

The main problem was that the database size could range from 50-150 gigs in size after finally being dumped from redis to disk, the next problem being this was a large file and we wanted to store this dump for a persistent amount of time and be able to pull these dumps down for development/analytics/restoration of a server in a said timely manner. With the size of these files, compression became a factoring issue because of cpu usage, after that hurdle was crossed uploading this to amazon became a secondary issue due to size. All these factors combined ended up tanking our redis instances. 

The next problem was save sets were too unpredictable in our cases, when we would configure redis to do saves on certain save values some would never trigger or some would trigger so often that they could queue processes and again result in back up processes running constantly. 

That is when this project was written, we needed a process to do abstract the backup process for us, manage it and do it on a timed basis so that it would handle without too much overhead on the production environment. 

Redis Backup manager was written very dirty and quickly in python to basically perform the following tasks:
* Initiate a backup on a timed bases.
* compress the backup into a archived date
* upload this backup to s3
* repeat this for multiple instances of redis on a box
* sleep for a duration between backups 


Configuration
--------------
a default block must always be present this sets the server blocks to look for an config settings

```
[default]
servers=server1,server2,server3
```

an AWS block must also always be present, this sets up the AWS credentials and bucket.
```
[aws]
aws_access_key=aaaa
aws_secret_key=bbbbb
s3_bucket=ccccc
```

For each server listed in servers, a server block with that title must be present that specifies the configuration.
```
[server1]
hostname=localhost #this is the host name to connect to
port=6379 # what redis port
redis_db_name=dump.rdb # what will the redis conf name the file when it saves
redis_save_dir=/tmp # redis data dir
prefix=none # if left as none it will use hostname and port name as a prefix, else can be used to specify a name
```
