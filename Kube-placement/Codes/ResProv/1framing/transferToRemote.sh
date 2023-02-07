#!/bin/bash

date +"%s.%3N" && \
for f in $(ls *.jpg)
do
#	scp -i ~/.ssh/authorized_keys2 $f edgegateway@143.205.122.37:/home/edgegateway/Documents/matching/Traffic-Sign-Classifier/FromLevono/frame-20000
#	scp -i ~/.ssh/authorized_keys2 $f pi@143.205.122.164:~/Documents/matching/Traffic-Sign-Classifier/FromLenovo/frame-20000
#	scp -i ~/.ssh/authorized_keys2 $f pi@143.205.122.155:~/Documents/matching/Traffic-Sign-Classifier/FromLenovo/frame-20000
#	scp -i "Lenovo2AWS.pem" $f ec2-user@ec2-18-144-62-160.us-west-1.compute.amazonaws.com:~/Documents/
	scp -i "t2xlarge.pem" $f ubuntu@ec2-34-201-127-36.compute-1.amazonaws.com:~/
done
date +"%s.%3N" &&  \
exit
