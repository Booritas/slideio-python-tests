#!/bin/bash
set -e

# Check if a command-line parameter is supplied
if [ -z "$1" ]; then
  echo "Error: No direcotry with slideio wheel files supplied."
  exit 1
fi

dists=$1

# Check if the directory exists
if [ ! -d "$dists" ]; then
  echo "Error: Directory '$dists' does not exist."
  exit 1
fi

# Save the command-line parameter in variable dists
dists=$1


# Check OS and platform
os=$(uname -s)
platform=$(uname -m)
minversion=7

if [[ "$os" == "Darwin" && "$platform" == "arm64" ]]; then
  # Set an environment variable if OS is macOS and platform is ARM
  minversion=8
fi


# Define an array of Python version strings
# Define a function to create an array of Python versions
generate_python_versions() {
   min_version=$1
   max_version=$2
   # Initialize an empty array
   python_versions=()
   # Loop from the minimum to the maximum version
   for ((version=min_version; version<=max_version; version++)); do
      python_versions+=("3.$version")
   done
   # Print the generated array
   echo ${python_versions[@]}
}

create_and_activate_conda_env() {
  version=$1
  # Create a conda environment for each Python version
  echo "Creating conda environment for Python $version"
  conda create -y -n "env_python_$version" python=$version
  # Activate the environment
  echo "Activating conda environment for Python $version"
  conda activate "env_python_$version"
}

deactivate_and_remove_conda_env() {
  version=$1
  # Deactivate the environment
  echo "Deactivating conda environment for Python $version"
  conda deactivate
  
  # Remove the environment
  echo "Removing conda environment for Python $version"
  conda remove -y -n "env_python_$version" --all
  echo "-----end of processing python version $version"
}

generate_python_versions minversion 12
rm -rf ./dist
eval "$(conda shell.bash hook)"

for version in "${python_versions[@]}"; do

   echo "-----processing python verion $version"

   create_and_activate_conda_env $version

   # Find and install the .whl file corresponding to the current Python version
   whl_file=$(find "$dists" -name "*cp${version//.}*.whl" | head -n 1)
   if [ -z "$whl_file" ]; then
     echo "Error: No .whl file found for Python $version in directory '$dists'"
     deactivate_and_remove_conda_env $version
     continue
   fi
   echo "Installing $whl_file"
   python -m pip install "$whl_file"

   python -m pip install -r ./requirements.txt
   pytest .
   
   deactivate_and_remove_conda_env $version
done