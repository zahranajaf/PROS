#!/bin/bash 
# arg1: input file
# arg2: output directory

input_file=${1}
input_directory=${2}
output_directory=${3}
mq_write=${4}

echo '#'
echo '#  Starting Process: '
echo '#'

python3 split.py "${input_file}" "${input_directory}"

echo '	Done'

# Loop through all files in argument list
for from_file_path in $(ls ${input_directory}/*.jpg)
do
    curr_file_name=${from_file_path##*/} 
    echo "	${curr_file_name}"
    to_file_path=${output_directory}
    #shift    

    cp ${from_file_path} ${to_file_path}

    # Write to message queue
    if [  "${mq_write}" != "-" ]; then
        echo "	Writing file name ${curr_file_name} to a message queue ${mq_write}"
        result="$(./write_to_mq.sh ${mq_write} ${curr_file_name})"
	  echo ${result}
    fi 
done
