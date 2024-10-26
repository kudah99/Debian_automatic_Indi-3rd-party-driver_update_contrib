#!/bin/bash

drivers=$(apt list --installed 2>/dev/null | grep -i "driver")

if [[ -z "$drivers" ]]; then
  echo "No driver packages found."
  exit 0
fi

while IFS= read -r driver; do
  package_name=$(echo "$driver" | cut -d/ -f1)

  version_info=$(apt-cache policy "$package_name" | grep 'Installed' | awk '{print $2}')

  if [[ -z "$version_info" ]]; then
    echo "No version information found for $package_name."
    continue
  fi

  debian_version=$(echo "$version_info" | cut -d'-' -f1)

  git_hash=$(echo "$version_info" | grep -oP '(?<=\.git\.)\w+' || echo "N/A")

  echo "Package: $package_name"
  echo "Debian Version: $debian_version"
  echo "Git Hash: $git_hash"
  echo "---------------------------------"
done <<< "$drivers"