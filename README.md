
[![License](http://img.shields.io/:license-affero-blue.svg)](http://www.gnu.org/licenses/agpl-3.0.en.html)

[![Build Status](https://travis-ci.org/Malfoy/BWISE.svg?branch=master)](https://travis-ci.org/Malfoy/BCOOL)


# BCOOL
de Bruijn graph cOrrectiOn from graph aLignment

[Limasset A, Flot J-F, Peterlongo P (2020) Toward perfect reads: self-correction of short reads via mapping on de Bruijn graphs. Bioinformatics 36:1374–1381](https://doi.org/10.1093/bioinformatics/btz102) 


## Dependencies
The installation script of Bcool compiles [Bcalm2](https://github.com/GATB/bcalm), [Bgreat2](https://github.com/Malfoy/BGREAT2), [Btrim](https://github.com/Malfoy/BTRIM) and [ntCard](https://github.com/bcgsc/ntCard).

This requires GCC>=4.9.1, CMAKE>=3.10, Autoconf, Automake and Python 3.

## Installation

`git clone https://github.com/Malfoy/BCOOL/`

`./install.sh`

For a faster install using 8 cores

`./install.sh -t 8`

## Test

`cd test`

`./test.sh`

Bcool will be tested with a fixed kmer size and with ntCard

It should output

`IT WORKS without ntcard !`

and

`IT WORKS with ntcard!`

If only the first message is present, you can still use Bcool but you need to give a size of k to perform correction.



## Usage

Standard command line

`./Bcool.py -u reads.fa -o workingDirectory`

With 20 cores

`./Bcool.py -u reads.fa -o workingDirectory -t 20`

With a fixed kmer size

`./Bcool.py -u reads.fa -o workingDirectory -k 63`


## Advanced options

### Graph construction
-s kmer filtering: kmer seen less than s time will not be included in the graph (default 2)

-S unitig filtering: unitig with abundance inferior to S will be removed from the graph prior correction (default 5)

### Alignment
-a anchor size: size of the seed of the alignment (default 41) lower value will increase sensibility and decrease throughput

-e mapping effort: number of different seed to test (default all) lower value will decrease sensibility and increase throughput

-m missmatches allowed: number of missmatches allowed for an alignment to be considered valid






