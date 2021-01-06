#!/bin/bash
# set -e

# Default values
n_iterations=3
flag_run_icn=0
flag_run_ip=0
flag_run_sdn=0
output_dir=""
topology_path=""
log_path="runSuite.log"

show_help () {

    echo -e "\n  runSuite: runs benchmark suite for ICN networks"
    echo "  Usage:
      ./runSuite -t <topology_path> <options> -o <output_path>
      The options are:
      -h: Show this
      -n: Overrides the number of iterations for each benchmark (default $n_iterations)

      By default, all three benchmarks are run. When any of the following parameters are passed, the behavior changes so that only those specified are run.
      --icn: Pure ICN benchmark
      --sdn: ICN + SDN benchmark
      --ip: IP benchmark
      
      -o: Output path for the resulting MiniNDN logs
      -t: Topology file 
      "
}

run_benchmark () {
    # $1 -> experiment type (sdn, icn, ip)
    # $2 -> experiment iteration
    echo "Experiment iteration $1 $2" >> $log_path
    sudo ./experiment_send.py -t $topology_path --$1
    mkdir -p $output_dir/icn/run$2
    sudo mv /tmp/minindn/* $output_dir/icn/run$2
}

echo "Starting" >> $log_path

# Read commmand line parameters
while getopts "h?n:?icn-:?sdn-:?ip-:?o:t:" opt; do
    case "$opt" in
    h|\?)
        show_help
        exit 0
        ;;
    n)
        n_iterations=$OPTARG
        echo "Number of iterations=$n_iterations"
        ;;
    o)
        output_dir=$OPTARG
        echo "Output path=$output_dir"
        ;;
    t)
        topology_path=$OPTARG
        ;; 
    -)
        case "${OPTARG}" in
            sdn)
                flag_run_sdn=1
                echo "SDN"
                ;;
            icn)
                flag_run_icn=1
                echo "ICN"
                ;;
            ip)
                flag_run_ip=1
                echo "IP"
                ;;
            *)
                echo "Unknown argument --${OPTARG}"
                ;;
        esac;;
    esac
done

# Decide which benchmarks to run
if [ "$flag_run_sdn" = 0 ] && [ "$flag_run_icn" = 0 ] && [ "$flag_run_ip" = 0 ]; then
    # If the benchmarks have not been specified, run all
    flag_run_sdn=1
    flag_run_icn=1
    flag_run_ip=1
fi

# Check output directory
if [ "$output_dir" != "" ]
then
    if [ ! -d "$output_dir" ]
    then
        mkdir $output_dir
    fi
else
    echo "ERROR: No output directory specified"
    show_help
    exit 0
fi

echo "About to run experiments with iterations=$n_iterations" >> $log_path
# Run experiments
for i in $(seq 1 $n_iterations)
do
    # SDN benchmark
    if [ "$flag_run_sdn" = 1 ]
    then
        run_benchmark "sdn" "$i"
    fi
    # ICN benchmark
    if [ "$flag_run_icn" = 1 ]
    then
        run_benchmark "icn" "$i"
    fi
    # IP benchmark
    if [ "$flag_run_ip" = 1 ]
    then
        run_benchmark "ip" "$i"
    fi
done

echo "Done!" >> $log_path
