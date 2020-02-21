#!/bin/bash


function get_optimisation_level()
{
	declare -a all_opt_capabilities=(avx avx2 fma sse sse2 ssse3 sse4_1 sse4_2)

	# Grab the flags
	flags=$(grep flags /proc/cpuinfo |head -1|cut -f2- -d:)

	declare -A flag_map
	# Create an associatve array and add to it
	for i in $flags
	do
		i=$(tr [A-Z] [a-z] <<< $i)
		flag_map[$i]=$i
	done
	echo "Gathered flags in map as follows: " ${!flag_map[@]}
	
	declare -i num_optimisations=0
	for cap in "${all_opt_capabilities[@]}"
	do
		if [[ ! -z "${flag_map[${cap}]}" ]]
		then
			num_optimisations=$(( num_optimisations	+ 1 ))
		fi
	done
	
	local -n optim_level=$1
	
	# If we found all capabilities, we flag it as "all"
	if [[ $num_optimisations -eq "${#all_opt_capabilities[*]}" ]]
	then
  		optim_level="all"
	elif [[ $num_optimisations -eq 0 ]]
	then
		optim_level="none"
	else
  		optim_level="safe"
	fi
}

function get_compute_engine_type()
{
    local -n engine_type=$1

	engine_type="cpu"
	if [[ ! -z ${CUDA_HOME+x} && -f $CUDA_HOME/lib64/libcudart.so ]]
	then
		cuda_version=$(cat ${CUDA_HOME}/version.txt | cut -d' ' -f3)
		if [[ $? -eq 0 ]]
		then
			echo "Determined CUDA verison to be $cuda_version"
			cuda_major_ver=$(echo $cuda_version | awk -F '.' '{print $1}')
			engine_type="cuda_${cuda_major_ver}"
		fi
	fi

}

function get_gcc_major_version()
{
    local -n gcc_version=$1
	gcc_version="gcc_$(gcc -dumpversion | cut -f1 -d.)"
}

function get_env_script_spec()
{
	OPTIM_LEVEL=""
	get_optimisation_level 'OPTIM_LEVEL'
	echo "Determined optimisation level to be $OPTIM_LEVEL"
	
	COMPUTE_ENGINE_TYPE=""
	get_compute_engine_type 'COMPUTE_ENGINE_TYPE'
	echo "Determined compute engine type to be $COMPUTE_ENGINE_TYPE"
	
	GCC_MAJOR_VERSION=""
	get_gcc_major_version 'GCC_MAJOR_VERSION'
	echo "Determined gcc major version  to be $GCC_MAJOR_VERSION"

    local -n env_script_spec=$1
	env_script_spec="$GCC_MAJOR_VERSION-$COMPUTE_ENGINE_TYPE-$OPTIM_LEVEL"
}


ENV_SCRIPT_SPEC=""
get_env_script_spec 'ENV_SCRIPT_SPEC'
echo "Determined env script spec to be $ENV_SCRIPT_SPEC"
