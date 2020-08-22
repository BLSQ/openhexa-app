#!/bin/bash

full_image_path=$1
tag=$2

if [ "$full_image_path" = "" ]; then
	echo "Please provide the full image path on the image repository"
	exit 1
fi

if [ "$tag" = "" ]; then
	echo "Please provide a tag for your image"
	exit 1
fi

echo "Building single-user server image $full_image_path:$tag..."

docker build -t habari-jupyter:latest jupyter
docker tag habari-jupyter:latest "$full_image_path:latest"
docker tag habari-jupyter:latest "$full_image_path:$tag"
docker push "$full_image_path:latest"
docker push "$full_image_path:$tag"

printf "\n"
echo "Done."
echo "Don't forget to update your project config files with the new \"$tag\" tag."
