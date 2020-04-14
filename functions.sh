UNAME=$(tr [A-Z] [a-z] <<< "$(uname)")
export SCRIPTS_DIR="$( cd "$( echo "${BASH_SOURCE[0]%/*}/" )"; pwd )"

function get_default_compiler()
{
	# Detect the platform (similar to $OSTYPE)
	OS="`uname`"
	case $OS in
  	'Linux')
		echo "gcc"
    	;;
  	'FreeBSD')
		echo "gcc"
    	;;
  	'WindowsNT')
		echo "msvcpp"
    	;;
  	'Darwin') 
		echo "apple_clang"
    	;;
  	'SunOS')
    	echo "gcc"
    	;;
  	'AIX') 
		echo "xlc"
    	;;
  	*)
		echo "UNKNOWN"
		;;
	esac
}

############################################################################
# Get the build spec 
#
# Syntax: get_extra_build_spec <compiler> <compute_engine> <optimization spec>
# e.g. get_extra_build_spec "gcc" "cpu" "all"
############################################################################
function get_extra_build_spec()
{
	local compiler=$1
	local compute_engine=$2
	local optim_spec=$3

	local build_spec="${compiler}-${compute_engine}-${optim_spec}"
	echo $build_spec
}

############################################################################
# Remove duplicates and things that don't exist
#
# Syntax: cleanup_path PATHNAME
############################################################################
cleanup_path()
{
    pathName=$1
    eval pathContents=\"\$$pathName\"
	newPath=$(echo -n $pathContents | awk -v RS=: '!($0 in a) {a[$0]; printf("%s%s", length(a) > 1 ? ":" : "", $0)}')
    eval "$pathName=$newPath"
}

############################################################################
# Exports Conan recipes from a given directory
#
# Syntax: conan_export <Conan channel> <Base Directory> <List of packages>
############################################################################
function do_conan_export()
{
	conan_channel=$1
	base_dir=$2
	libs_to_build=$3
	ret=""
	
	myName=$(basename $0)
	for i in ${libs_to_build}
	do
		dir="${base_dir}/${i}"
		if [[ ! -d "${dir}" ]]
		then
			dir="${base_dir}/conan-${i}"
		fi

		if [[ -d ${dir} ]]
		then
			dirBase="$(basename -- ${dir})"
			echo "Exporting recipe for package $dirBase"

			conan export ${dir} ${conan_channel}
		fi
	done

	return 0
}

######################################################################################
# Wraps the git binary in a shell script that ensures that it uses the shared libraries 
# it was built with Wraps the git binary in a shell script that ensures that it uses the shared libraries 
# it was built with.
######################################################################################
function git()
{
	unset git &> /dev/null 
	unalias git &> /dev/null
	unset -f git &> /dev/null


    gitRealPath=$(command -v git.exe)
    declare -A git_libs

	for i in `ldd ${gitRealPath} | grep so | sed -e '/^[^\t]/ d' | sed -e 's/\t//' | sed -e 's/.*=..//' | sed -e 's/ (0.*)//' | sort | uniq`
    do
        lib_dir=$(dirname $i)
        echo $lib_dir
        if [[ $lib_dir == /* ]]
        then
            git_libs["$lib_dir"]="$lib_dir"
        fi
    done

    lib_path=""
    for x in "${!git_libs[@]}"
    do  
        printf "[%s]=%s\n" "$x" "${git_libs[$x]}"
        
        if [[ ${lib_path} == "" ]]
        then
            lib_path=$x
        else
            lib_path="$lib_path:$x"
        fi
    done

    cmd="LD_LIBRARY_PATH=${lib_path};DYLD_LIBRARY_PATH=${lib_path} ${gitRealPath} $@"
	echo "Running git with adjusted LIBRARY paths variables as $cmd"
	eval ${cmd}
} 

######################################################################################
# Installs a given set of Conan recipes
#
# Syntax: do_conan_install <conanfile> <Conan channel> <build type> <compiler> <compute engine> \
#                          <optimization spec> <Conan profile> <Conan install folder>
######################################################################################
function do_conan_install()
{
	conanfile_txt=$1
	conan_channel=$2
	build_type=$3
	compiler=$4
	compute_engine=$5
	optim_spec=$6
	profile_file=$7
	install_folder=$8
	
	if ! [[ "$optim_spec" =~ ^(all|safe|none)$ ]]
	then
		echo "Error: unknown optimisation level '$optim_spec'"
		return 1
	fi
	
	if ! [[ "$compute_engine" =~ ^(cpu|cuda_10)$ ]]
	then
		echo "Error: unknown compute engine type '$compute_engine'"
		return 1
	fi
	
	if [ "x$compiler" = "x" ]
	then
		echo "Error: no compiler specified"
		return 1
	fi

	echo "Using profile '$profile_file' for building"
	if [ ! -f "$profile_file" ]
	then
		echo "Error: profile file $profile_file does not exist"
		return 1
	fi
	
	if [ ! -f "$conanfile_txt" ]
	then
		echo "Error: conanfile $conanfile_txt does not exist"
		return 1
	fi

	extra_build_spec=$(get_extra_build_spec $compiler $compute_engine $optim_spec)
	install_folder=${CONAN_USER_HOME}/CMakeModules/${extra_build_spec}
	
	conan_build_options="--settings build_type=${build_type}"
	conan_profile_options="--profile=${profile_file}"
	conan_install_options="--install-folder=${install_folder}"
	
	echo "Installing all conan components using confile ${conanfile_txt}"
	conan install ${conan_profile_options} ${conan_install_options} ${conan_build_options} ${conan_build_cpp_options} --build outdated ${conanfile_txt}

	return 0
}
