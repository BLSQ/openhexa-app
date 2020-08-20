#!/bin/sh

project=$1

if [ "$project" = "" ]; then
	echo "Please provide a project name"
	exit 1
fi

echo "Deploying project $project"

# TODO: --create-namespace should be an option
helm upgrade --install "habari-$project" jupyterhub/jupyterhub \
  --namespace "$project" \
  --create-namespace \
  --version=0.9.0 \
  --values config.yaml \
  --values config/"$project".yaml

hub_ip=$(kubectl get svc proxy-public --namespace="$project" -o jsonpath="{.status.loadBalancer.ingress[*].ip}")

printf "\n"
echo "Done."
echo "Hub deployed at $hub_ip"
