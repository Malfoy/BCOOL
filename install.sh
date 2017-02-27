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
SCRIPT=$(readlink -f $0)
# Absolute path this script is in. /home/user/bin
folder=`dirname $SCRIPT`
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
echo "I put binaries in $folder"



make LOL=-Dfolder=$folder -j $threadNumber >>logCompile 2>>logCompile;
cp bcool ..;
echo PHASE ZERO LAUNCHER: BCOOL;



git clone --recursive https://github.com/GATB/bloocoo.git >>logCompile 2>>logCompile;
cd bloocoo;
mkdir build32; cd build32;
cmake -DKSIZE_LIST="32" .. >>logCompile 2>>logCompile;
make -j $threadNumber >>logCompile 2>>logCompile;
cp bin/Bloocoo Bloocoo32;
cp Bloocoo32 $folder;
#~ cd ..;
#~ mkdir build64; cd build64;
#~ cmake -DKSIZE_LIST="64" .. >>logCompile 2>>logCompile;
#~ make -j $threadNumber >>logCompile 2>>logCompile;
#~ cp bin/Bloocoo Bloocoo64;
#~ cp Bloocoo64 $folder;
#~ cd ..;
#~ mkdir build128; cd build128;
#~ cmake -DKSIZE_LIST="128" .. >>logCompile 2>>logCompile;
#~ make -j $threadNumber >>logCompile 2>>logCompile;
#~ cp bin/Bloocoo Bloocoo128;
#~ cp Bloocoo128 $folder;
cd ../..;
cp bloocoo/build32/ext/gatb-core/bin/h5dump $folder;



echo PHASE ONE, READ CORRECTION: BLOOCOO;



git clone --recursive https://github.com/GATB/bcalm >>logCompile 2>>logCompile;
cd bcalm;
mkdir build; cd build;
cmake -DKSIZE_LIST="32 64 96 128 160" ..  >>logCompile 2>>logCompile;
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



git clone https://github.com/kamimrcht/kMILL >>logCompile 2>>logCompile;
cd kMILL/src;
make -j $threadNumber >>logCompile 2>>logCompile;
cp kMILL $folder;
cp sequencesCleaner $folder;
cp tipCleaner $folder;
cd ../..;
echo PHASE FOUR, Sequences cleaning: KMILL;



echo The end !;

