#!/bin/bash
# set -e

# Default values
n_iterations=3
flag_run_icn=0
flag_run_ip=0
flag_run_sdn=0
output_dir=""
topology_path=""

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

for i in $(seq 1 $n_iterations)
do
    # sudo ./experiment_send.py $topology_path --icn
    mkdir -p $output_dir/icn/run$i
    sudo mv /tmp/minindn/* $output_dir/icn/run$i

    # sudo ./experiment_send.py $topology_path --sdn
    # mkdir -p $output_dir/sdn/run$i
    # sudo ./experiment_send.py $topology_path --ip
    # mkdir -p $output_dir/ip/run$i
done

# sudo ./draw_topology.py $topology_path






# # Show Galileo dirs containing the script
# if [ $show_g_dirs -eq 1 ]
# then
#     ssh root@"$galileo_name" 'echo -e "\n\t~/init_scripts";
#         ls -l ~/init_scripts;
#         echo -e "\n\t/etc/init.d";
#         ls -l /etc/init.d;
#         echo -e "\n\t/etc/rc0.d";
#         ls -l /etc/rc0.d'
#     exit 1
# fi

# # Manage Galileo scripts
# basename=$(basename "$script_path")

# if [ $flag_remove -eq 0 ]
# then
#     # Add script
#     if [ ! -f "$script_path" ]; then echo "Error, file '"$script_path"' does not exist!"; exit 0; fi;
#     scp "$script_path" root@"$galileo_name":~/init_scripts
#     ssh root@"$galileo_name" 'cd ~/init_scripts;
#         cp '$basename' /etc/init.d;
#         chmod +x /etc/init.d/'$basename';
#         update-rc.d '$basename' defaults;
#         reboot'
# else
#     # Remove script
#     ssh root@"$galileo_name" 'cd /etc/init.d;
#         update-rc.d -f '$basename' remove'
# fi