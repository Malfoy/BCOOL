#!/bin/bash



#THIS INSTALLATION REQUIRES GCC, GIT, MAKE, CMAKE



function help {
echo "BCOOL installation script"
echo "This installation requires GCC>=4.9, GIT, MAKE and CMAKE3"
echo "-f absolute path of folder to put the binaries"
echo "-t to use multiple thread for compilation (default 8)"
}


cd src;


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




git clone --recursive https://github.com/GATB/bloocoo.git ;
cd bloocoo;
mkdir build32; cd build32;
cmake -DKSIZE_LIST="32" .. ;
make -j $threadNumber ;
mv bin/Bloocoo Bloocoo32;
cp Bloocoo32 $folder;
cd ../..;




echo PHASE ONE, READ PreCORRECTION: BLOOCOO;



git clone --recursive https://github.com/GATB/bcalm ;
cd bcalm;
mkdir build; cd build;
cmake -DKSIZE_LIST="32 64 128" ..  ;
make -j $threadNumber ;
cp bcalm $folder;
cd ../..;
echo PHASE TWO, GRAPH CONSTRUCTION: BCALM;



git clone https://github.com/Malfoy/BGREAT2 ;
cd BGREAT2;
make -j $threadNumber ;
cp bgreat $folder;
cd ..;
echo PHASE THREE, READ MAPPING ON THE DBG: BGREAT;


git clone https://github.com/Malfoy/BTRIM ;
cd BTRIM;
make -j $threadNumber;
if [ $? -ne 0 ]
       then
              echo "there was a problem with btrim compilation, check logs"
              exit 1
       fi
cp btrim $folder;
cd ..;
echo PHASE FOUR GRAPH CLEANING: BTRIM;


cd .. ;
tar -czvf bin.tar.gz $folder ;



echo The end !;

