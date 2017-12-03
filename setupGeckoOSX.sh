#!/bin/bash

echo '*******************************'
echo 'get gecko latest release'
echo '*******************************'

GECKO_VERSION=$(curl -sS https://github.com/mozilla/geckodriver/releases/latest | grep -o -e 'v[0-9].[0-9][0-9].[0-9]')
echo "Installing gecko for Mac version ${GECKO_VERSION}"

mkdir -p /tmp/geckodriver
pushd /tmp/geckodriver > /dev/null

GECKO_PATH=https://github.com/mozilla/geckodriver/releases/download/${GECKO_VERSION}/geckodriver-${GECKO_VERSION}-macos.tar.gz
echo "Pulling down ${GECKO_PATH}"

wget ${GECKO_PATH}
tar -zxf geckodriver-${GECKO_VERSION}-macos.tar.gz -C /tmp/geckodriver
chmod +x ./geckodriver
mv -f ./geckodriver /usr/local/bin
popd  > /dev/null
rm -rf /tmp/geckodriver

SUCCESS=$(/usr/local/bin/geckodriver --version | grep -o 'geckodriver [0-9].[0-9][0-9].[0-9]')
echo "Installed ${SUCCESS}"