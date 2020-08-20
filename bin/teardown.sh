#!/bin/sh

project=$1

if [ "$project" = "" ]; then
	echo "Please provide a project name"
	exit 1
fi

echo "Tearing down project $project"

helm uninstall habari --namespace "$project"
kubectl delete namespace "$project"

printf "\n"
echo "Done."
echo "Please make sure to cleanup all the associated resources in your cloud provider environment."
echo "This include clusters, disks, images, load balances, etc..."