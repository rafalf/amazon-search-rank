#!/bin/bash

echo '*******************************'
echo 'get chromedriver latest release'
echo '*******************************'

CHROMEDRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE)
echo "Installing chromedriver for Mac version ${CHROMEDRIVER_VERSION}"

mkdir -p /tmp/chromedriver
pushd /tmp/chromedriver > /dev/null
curl -sO https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_mac64.zip
unzip -oq ./chromedriver_mac64.zip -d .
chmod +x ./chromedriver
mv -f ./chromedriver /usr/local/bin
popd  > /dev/null
rm -rf /tmp/chromedriver

SUCCESS=$(/usr/local/bin/chromedriver --version)
echo "Installed ${SUCCESS}"
