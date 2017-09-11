#!/bin/bash



#THIS INSTALLATION REQUIRES GCC, GIT, MAKE, CMAKE



function help {
echo "BCOOL installation script"
echo "This installation requires GCC>=4.9, GIT, MAKE and CMAKE3"
echo "-f absolute path of folder to put the binaries"
echo "-t to use multiple thread for compilation (default 8)"
}


#~ mkdir src;
#~ cd src;

threadNumber=8
folder=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
folder+="/bin"


while getopts "hf:t:" opt; do
case $opt in
h)
help
exit
;;
f)
echo "use folder: $OPTARG" >&2
folder=$OPTARG
;;
s)
echo "use  $OPTARG threads" >&2
threadNumber=$OPTARG
;;
\?)
echo "Invalid option: -$OPTARG" >&2
exit 1
;;
:)
echo "Option -$OPTARG requires an argument." >&2
exit 1
;;
esac
done

if [ -z "$folder"  ]; then
	help
	exit 0
	fi



mkdir $folder;
echo "I put binaries in $folder";




git clone --recursive https://github.com/bcgsc/ntCard >>logCompile 2>>logCompile;
cd ntCard;
./autogen.sh >>logCompile 2>>logCompile;
./configure CFLAGS='-g -O3' CXXFLAGS='-g -O3' >>logCompile 2>>logCompile;
make -j $threadNumber >>logCompile 2>>logCompile;
cp ntcard $folder;
cd ..;
echo PHASE ONE, kmer spectrum estimator ntcard;



git clone --recursive https://github.com/GATB/bcalm >>logCompile 2>>logCompile;
cd bcalm;
mkdir build; cd build;
cmake -DKSIZE_LIST="32 64 128" ..  >>logCompile 2>>logCompile;
make -j $threadNumber >>logCompile 2>>logCompile;
cp bcalm $folder;
cd ../..;
echo PHASE TWO, GRAPH CONSTRUCTION: BCALM;



git clone https://github.com/Malfoy/BGREAT2 >>logCompile 2>>logCompile;
cd BGREAT2;
make -j $threadNumber >>logCompile 2>>logCompile;
cp bgreat $folder;
cd ..;
echo PHASE THREE, READ MAPPING ON THE DBG: BGREAT;


git clone https://github.com/Malfoy/BTRIM >>logCompile 2>>logCompile;
cd BTRIM;
make -j $threadNumber >>logCompile 2>>logCompile;
if [ $? -ne 0 ]
       then
              echo "there was a problem with btrim compilation, check logs"
              exit 1
       fi
cp btrim $folder;
cp badvisor $folder;
cd ..;
echo PHASE FOUR GRAPH CLEANING: BTRIM;




echo The end !;

