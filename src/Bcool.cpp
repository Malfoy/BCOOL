#include <iostream>
#include <fstream>
#include <chrono>
#include <string>
#include <unistd.h>
#include <vector>
#include <chrono>
#include <stdlib.h>



#define XSTR(x) #x
#define STR(x) XSTR(x)



using namespace std;
using namespace chrono;



void help(){
	cout<<"BCOOL"<<endl
	<<"Options and default values: "<<endl
	<<"-u for read file"<<endl
	<<"-o for working folder (.)"<<endl
	<<"-k for  kmer size (51)"<<endl
	<<"-s for kmer solidity threshold (2)"<<endl
	<<"-l tipping length (100)"<<endl
	<<"-t for core used (max)"<<endl
	<<"-c for correction step (1)"<<endl
	;
}



int main(int argc, char *argv[]) {
	if(argc<2){
		help();
		exit(0);
	}
	string unPairedFile(""),workingFolder("."),prefixCommand(""),folderStr(STR(folder)),bgreatArg,bloocooArg,slowParameter("-slow");
	uint k(51),solidity(2),coreUsed(0),correctionStep(1),tipLength(100);
	if(folderStr!=""){
		prefixCommand=folderStr+"/";
	}
	char c;
	while ((c = getopt (argc, argv, "u:x:o:s:k:p:c:t:S:l:")) != -1){
	switch(c){
		case 'u':
			unPairedFile=realpath(optarg,NULL);
			break;
		case 'o':
			workingFolder=(optarg);
			break;
		case 's':
			solidity=stoi(optarg);
			break;
		case 'k':
			k=stoi(optarg);
			break;
		case 'l':
			tipLength=stoi(optarg);
			break;
		case 't':
			coreUsed=stoi(optarg);
			break;
		case 'c':
			correctionStep=stoi(optarg);
			break;
		}
	}
	if(unPairedFile==""){
		help();
		exit(0);
	}
	c=system(("mkdir "+workingFolder).c_str());
	c=chdir(workingFolder.c_str());
	c=system("mkdir logs");
	ofstream param("ParametersUsed.txt");
	ofstream bankBcalm("bankBcalm.txt");
	param<<"k: "<<k<<" solidity: "<<solidity<<endl;
	bloocooArg=unPairedFile;
	bgreatArg=" -u reads_corrected.fa ";
	bankBcalm<<"reads_corrected.fa"<<endl;
	auto start=system_clock::now();

	//CORRECTION
	auto point1=system_clock::now();
	cout<<"Reads pre-Correction"<<endl;
	string fileToCorrect(unPairedFile);
	vector<string> kmerSizeCorrection={"31","63","95","127"};
	vector<string> bloocooversion={"32","64","128","128"};
	uint indiceCorrection(0);
	for(;indiceCorrection<min(correctionStep,(uint)kmerSizeCorrection.size());++indiceCorrection){
		c=system((prefixCommand+"Bloocoo"+bloocooversion[indiceCorrection]+" -file "+bloocooArg+" "+slowParameter+" -abundance-min 10  -kmer-size "+kmerSizeCorrection[indiceCorrection]+" -nbits-bloom 24  -out reads_corrected"+to_string(indiceCorrection)+".fa -nb-cores "+to_string(coreUsed)+"  >>logs/logBloocoo 2>>logs/logBloocoo").c_str());
		c=system((prefixCommand+ "h5dump -y -d histogram/histogram  reads_corrected"+to_string(indiceCorrection)+".fa.h5  > logs/histocorr"+to_string(indiceCorrection)).c_str());
		c=system(("rm  reads_corrected"+to_string(indiceCorrection-1)+"* 2>> logs/histocorr"+to_string(indiceCorrection)).c_str());
		bloocooArg="reads_corrected"+to_string(indiceCorrection)+".fa ";
	}
	if(correctionStep==0){
		c=system(("ln -s "+bloocooArg+" reads_corrected.fa").c_str());
	}else{
		c=system(("mv "+bloocooArg+" reads_corrected.fa").c_str());
	}

	//GRAPH CONSTRUCTION
	auto point2=system_clock::now();
	cout<<"Pre-Correction took "<<duration_cast<seconds>(point2-point1).count()<<" seconds"<<endl;
	string fileBcalm("bankBcalm.txt"),kmerSize(to_string(k));
	cout<<"Graph construction "<<endl;
	string kmerSizeTip((to_string(tipLength)));
	c=system((prefixCommand+"bcalm -in "+fileBcalm+" -kmer-size "+kmerSize+" -abundance-min "+to_string(solidity)+" -out out  -nb-cores "+to_string(coreUsed)+"  >>logs/logBcalm 2>>logs/logBcalm").c_str());
	//~ c=system((prefixCommand+ "h5dump -y -d histogram/histogram  out.h5  > logs/histodbg"+(kmerSize)).c_str());
	c=system((prefixCommand+"kMILL out.unitigs.fa $(("+kmerSize+"-1)) $(("+kmerSize+"-2)) >>logs/logBcalm 2>>logs/logBcalm").c_str());
	c=system((prefixCommand+"tipCleaner out_out.unitigs.fa.fa $(("+kmerSize+"-1)) "+kmerSizeTip+" >>logs/logTip 2>>logs/logTip").c_str());
	c=system((prefixCommand+"kMILL tiped.fa $(("+kmerSize+"-1)) $(("+kmerSize+"-2)) >>logs/logBcalm 2>>logs/logBcalm").c_str());
	c=system(("mv out_tiped.fa.fa dbg.fa"));

	//GRAPH MAPPING
	auto point3=system_clock::now();
	cout<<"Building DBG took "<<duration_cast<seconds>(point3-point2).count()<<" seconds"<<endl;
	cout<<"Read mapping on the graph "<<endl;
	c=system((prefixCommand+"bgreat -k "+to_string(k)+"  "+bgreatArg+" -g dbg.fa -t "+to_string((coreUsed==0)?10:coreUsed) +" -f readCooled.fa  -m 10 -e 100 -O -c >>logs/logBgreat 2>>logs/logBgreat").c_str());
	//~ c=system((prefixCommand+"bgreat -k "+kmerSize+" -u  "+unPairedFile+" -g dbg.fa -t "+to_string((coreUsed==0)?10:coreUsed) +" -f readCooled.fa  -m 5 -e 2 -O -c >>logs/logBgreat 2>>logs/logBgreat").c_str());

	c=system(("rm *.h5 bankBcalm.txt  out_out.unitigs.fa.fa  out.unitigs.fa tiped.fa"));
	auto end=system_clock::now();
	cout<<"Mapping on DBG took "<<duration_cast<seconds>(end-point3).count()<<" seconds"<<endl;
    auto waitedFor=end-start;
    cout<<"Whole process took "<<duration_cast<seconds>(waitedFor).count()<<" seconds"<<endl;
	cout<<"The end"<<endl;
    return 0;
}
