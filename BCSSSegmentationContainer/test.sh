#!/usr/bin/env bash

SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"

./build.sh

VOLUME_SUFFIX=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 8 | head -n 1)

echo $VOLUME_SUFFIX
echo $SCRIPTPATH

docker volume create bcsssegmentationcontainer-output-$VOLUME_SUFFIX

echo "gothere"

docker run --rm \
        -v $SCRIPTPATH/test/:/input/ \
        -v bcsssegmentationcontainer-output-$VOLUME_SUFFIX:/output/ \
        bcsssegmentationcontainer

# docker run --rm \
#         -v bcsssegmentationcontainer-output-$VOLUME_SUFFIX:/output/ \
#         python:3.9-slim cat /output/results.json | python -m json.tool

docker run --rm \
        -v bcsssegmentationcontainer-output-$VOLUME_SUFFIX:/output/ \
        -v $SCRIPTPATH/test/:/input/ \
        python:3.9-slim python -c """
        expected_output = SimpleITK.ReadImage('expected_output/expected_output.tif')
        output = SimpleITK.ReadImage('output/output.tif')

        label_filter = SimpleITK.LabelOverlapMeasuresImageFilter()
        label_filter.Execute(output, expected_output)
        dice_score = label_filter.GetDiceCoefficient()

        if dice_score == 1.0:
            print('test worked')
        else:
            print('test failed')
        """
docker volume rm bcsssegmentationcontainer-output-$VOLUME_SUFFIX
