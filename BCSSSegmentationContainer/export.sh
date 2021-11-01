#!/usr/bin/env bash

./build.sh

docker save bcsssegmentationcontainer | gzip -c > BCSSSegmentationContainer.tar.gz
