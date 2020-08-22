#!/bin/bash

project=$1

if [ "$project" = "" ]; then
	echo "Please provide a project name"
	exit 1
fi

echo "Tearing down project $project..."
read -p "This will delete the $project namespace and all its resources. Are you sure? (y/N) "
if [[ $REPLY =~ ^[Yy]$ ]]
then
    helm uninstall "habari-$project" --namespace "$project"
    kubectl delete namespace "$project"
    echo "Done."
    echo "Please make sure to cleanup all the associated resources in your cloud provider environment."
    echo "This include clusters, disks, images, load balances, etc..."
else
  echo "Cancelled."
fi
