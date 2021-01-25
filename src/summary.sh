#!/bin/bash

##################################################################
#
# Generates a summary of all experiments whose consumerLogs are
# located in the specified result directory. This summary contains
# the output of the read_consumer_results.py script organized into
# network type and iteration.
#
# Andre Dexheimer Carneiro      07/12/2021
#
#################################################################

show_help () {

    echo -e "summary.sh : creates a text file with the output of read_consumer_results for all results in the specified directory"
    echo "  Usage: ./summary.sh <result_dir> <?output_file>"
    echo "  If no output file is especified, stdout will be used"
}

read_network_results () {
  # $1 -> directory containing the directories for each run
  for file_name in $(ls $1)
  do
    if [[ "$file_name" == "run"* ]]
    then
      results_path="$1$file_name/"
      echo -e "\nResults from path=$results_path"
      ./read_consumer_results.py $results_path
    fi
  done
}

# Check parameter 1, result dir path
if [ -z $1 ]
then
  show_help
  exit 1
else
  result_path=$1
fi

# Read and write ICN results
for file_name in $(ls $result_path)
do
  if [ $file_name == "icn" ]
  then
    echo -e "\n\nResults for ICN --------------------------------------------------"
    read_network_results "$1$file_name/"
  fi
done

# Read and write SDN results
for file_name in $(ls $result_path)
do
  if [ $file_name == "sdn" ]
  then
    echo -e "\n\nResults for SDN --------------------------------------------------"
    read_network_results "$1$file_name/"
  fi
done

# Read and write IP results
for file_name in $(ls $result_path)
do
  if [ $file_name == "ip" ]
  then
    echo -e "\n\nResults for IP --------------------------------------------------"
    read_network_results "$1$file_name/"
  fi
done
