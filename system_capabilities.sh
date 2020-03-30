#############################################################################################
#
#############################################################################################
function get_optimisation_level()
{
	# Detect the platform (similar to $OSTYPE)
    local OS="`uname`"
    case $OS in
    'Linux')
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
		
		local optim_level=$1
		
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

		eval "$1=$optim_level"
		;;
	*)
        eval "$1=all"
        ;;
    esac
}

#############################################################################################
#
#############################################################################################
function get_compute_engine_type()
{
    local engine_type=$1
	engine_type="cpu"

	if [[ ! -z ${CUDA_HOME+x} && -f $CUDA_HOME/lib64/libcudart.so ]]
	then
		# Run the nvidia-detector utility and test the return code
		nvidia_found=$(lspci | grep -i nvidia | wc -l)
		if [[ $? -eq 0 ]]
		then
			echo "Found CUDA driver version $nvidia_driver_version"

			cuda_version=$(cat ${CUDA_HOME}/version.txt | cut -d' ' -f3)
			if [[ $? -eq 0 ]]
			then
				echo "Determined CUDA version to be $cuda_version"
				cuda_major_ver=$(echo $cuda_version | awk -F '.' '{print $1}')
				engine_type="cuda_${cuda_major_ver}"
			fi
		fi
	fi

	eval "$1=$engine_type"
}

#############################################################################################
#
#############################################################################################
function get_compiler()
{
    # Detect the platform (similar to $OSTYPE)
    local OS="`uname`"
    case $OS in
    'Linux')
		local gcc_version="gcc_$(gcc -dumpversion | cut -f1 -d.)"
		eval "$1=$gcc_version"
        ;;
    'FreeBSD')
		local gcc_version="gcc_$(gcc -dumpversion | cut -f1 -d.)"
		eval "$1=$gcc_version" 
        ;;
    'WindowsNT')
		eval "$1=msvcpp" 
        ;;
    'Darwin')
		eval "$1=apple_clang" 
        ;;
    'SunOS')
        local gcc_version="gcc_$(gcc -dumpversion | cut -f1 -d.)"
		eval "$1=$gcc_version"
        ;;
    'AIX')
        val "$1=xlc_r" 
        ;;
    *)
        eval "$1=UNKNOWN"
        ;;
    esac
}

#############################################################################################
#
#############################################################################################
function get_env_spec()
{
	local COMPILER=$1
	local COMPUTE_ENGINE_TYPE=$2
	local OPTIM_LEVEL=$3

    local env_script_spec="$COMPILER-$COMPUTE_ENGINE_TYPE-$OPTIM_LEVEL"

	echo $env_script_spec
}

#############################################################################################
#
#############################################################################################
function compute_env_script_spec()
{
	local OPTIM_LEVEL=""
	get_optimisation_level 'OPTIM_LEVEL'
	echo "Determined optimisation level to be $OPTIM_LEVEL"
	
	local COMPUTE_ENGINE_TYPE=""
	get_compute_engine_type 'COMPUTE_ENGINE_TYPE'
	echo "Determined compute engine type to be $COMPUTE_ENGINE_TYPE"
	
	local COMPILER=""
	get_compiler 'COMPILER'
	echo "Determined compiler to be $COMPILER"

    local env_script_spec=$(get_env_spec $COMPILER $COMPUTE_ENGINE_TYPE $OPTIM_LEVEL)
	echo "Determined env spec to be $env_script_spec"

	eval "$1=$env_script_spec"
}

#############################################################################################
#
#############################################################################################
function get_no_opt_cpu_env_script_spec()
{
    local OPTIM_LEVEL="none"
    local COMPUTE_ENGINE_TYPE="cpu"
    local COMPILER=""
    get_compiler 'COMPILER'

    local env_script_spec=$1
	env_script_spec=$(get_env_spec $COMPILER $COMPUTE_ENGINE_TYPE $OPTIM_LEVEL)

    eval "$1=$env_script_spec"
}

#############################################################################################
#
#############################################################################################
function get_safe_cpu_env_script_spec()
{
    local OPTIM_LEVEL="safe"
    local COMPUTE_ENGINE_TYPE="cpu"
    local COMPILER=""
    get_compiler 'COMPILER'

    local env_script_spec=$1
	env_script_spec=$(get_env_spec $COMPILER $COMPUTE_ENGINE_TYPE $OPTIM_LEVEL)

    eval "$1=$env_script_spec"
}

#############################################################################################
#
#############################################################################################
function get_all_opt_cpu_env_script_spec()
{
    local OPTIM_LEVEL="all"
    local COMPUTE_ENGINE_TYPE="cpu"
    local COMPILER=""
    get_compiler 'COMPILER'

    local env_script_spec=$1
	env_script_spec=$(get_env_spec $COMPILER $COMPUTE_ENGINE_TYPE $OPTIM_LEVEL)

    eval "$1=$env_script_spec"
}

#############################################################################################
#
#############################################################################################
function run_env_script_spec()
{
	local env_script_spec=$1

	local conan_script_home="${CONAN_USER_HOME}/CMakeModules/${env_script_spec}"
	envSetupScript="${conan_script_home}/activate_run.sh"
	
	if [ -f "${envSetupScript}" ]
	then
		export CONAN_SCRIPT_HOME=$conan_script_home
    	. "${envSetupScript}"
		return 0
	fi

	return 1
}

#############################################################################################
#
#############################################################################################
function set_env_script()
{
	local run_env_script_spec
	compute_env_script_spec 'run_env_script_spec'
	echo "Determined env script spec to be $run_env_script_spec"

	run_env_script_spec $run_env_script_spec
	if [[ $? -eq 0 ]]
	then
		return 0
	fi

	local engine_type_1
	get_compute_engine_type 'engine_type_1'
	echo "Determined engine type to be $engine_type_1"

	local compiler
	get_compiler 'compiler'

	if [ "$engine_type_1" != "cpu" ]
	then
		run_env_script_spec=$(get_env_spec $compiler $engine_type_1 "all")
		echo "Testing for env script spec $run_env_script_spec"

		run_env_script_spec $run_env_script_spec
		if [[ $? -eq 0 ]]
		then
			return 0
		fi

		run_env_script_spec=$(get_env_spec $compiler $engine_type_1 "safe")
		echo "Testing for env script spec $run_env_script_spec"
		run_env_script_spec $run_env_script_spec
		if [[ $? -eq 0 ]]
		then
			return 0
		fi

		run_env_script_spec=$(get_env_spec $compiler $engine_type_1 "none")
		echo "Testing for env script spec $run_env_script_spec"
		run_env_script_spec $run_env_script_spec
		if [[ $? -eq 0 ]]
		then
			return 0
		fi
	fi

	run_env_script_spec=$(get_env_spec $compiler "cpu" "all")
	echo "Testing for env script spec $run_env_script_spec"
	run_env_script_spec $run_env_script_spec
	if [[ $? -eq 0 ]]
	then
		return 0
	fi

	run_env_script_spec=$(get_env_spec $compiler "cpu" "safe")
	echo "Testing for env script spec $run_env_script_spec"
	run_env_script_spec $run_env_script_spec
	if [[ $? -eq 0 ]]
	then
		return 0
	fi

	run_env_script_spec=$(get_env_spec $compiler "cpu" "none")
	echo "Testing for env script spec $run_env_script_spec"
	run_env_script_spec $run_env_script_spec
	if [[ $? -eq 0 ]]
	then
		return 0
	fi

	return 1
}
