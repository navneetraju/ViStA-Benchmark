!#usr/bin/env/ bash

echo "Installing dependencies"
apt install automake -y
apt install bison -y
apt install libtool -y
apt install libasound2-dev -y
apt install libpulse-dev -y
echo "Installing sphinxbase"
git clone https://github.com/cmusphinx/sphinxbase.git 
cd sphinxbase
./autogen.sh
./configure
make 
make check
make install
cd ..
echo "Now installing pocketsphinx"
git clone https://github.com/cmusphinx/pocketsphinx.git
cd pocketsphinx
./autogen.sh
./configure
make clean all
make check
make install
