#!/bin/bash
output_file_path=$1
PATH_TO_CREDENTIAL_FILE=""
namespace="hexa-app"

# Export variables from output file
terraform output >> "$output_file_path"
if ( ! ( sed -i 's/ //g' "$output_file_path" && sed -i 's/"//g' "$output_file_path" ) ) 
then 
    echo "Sed Failure!"
    exit 1
fi
. $output_file_path

# Get the connection string of your Cloud SQL instance and add it into $output_file_path
gcloud sql instances describe $gcp_sql_database_name  >> test.yaml
ConnectionName=$(yq -r .connectionName test.yaml)
rm test.yaml
echo CLOUDSQL_CONNECTION_STRING=$ConnectionName >> "$output_file_path"

# Make sure that the kubectl utility can access the newly created cluster
gcloud container clusters get-credentials $gcp_gke_cluster_name --zone $gcp_gke_cluster_zone
 
# Create a specific Kubernetes namespacz
kubectl create namespace $namesapce

# Create a secret for the Cloud SQL proxy
kubectl create secret generic cloudsql-oauth-credentials -n $namesapce \
   --from-file=credentials.json=$PATH_TO_CREDENTIAL_FILE

# Generate a secret key for the Django app
SECRET_KEY=$(docker-compose run app manage generate_secret_key)

# Create a secret for the Django environment variables
kubectl create secret generic app-secret -n $namesapce \
  --from-literal DATABASE_USER=$gcp_sql_database_password\
  --from-literal DATABASE_PASSWORD=$gcp_sql_database_password \
  --from-literal DATABASE_NAME=$gcp_sql_database_password \
  --from-literal DATABASE_PORT=5432 \
  --from-literal SECRET_KEY=$SECRET_KEY

# Copy the sample file
cp k8s/app.yaml.dist k8s/app.yaml

# Transform output file to YAML
if ( ! ( sed -i 's/=/: /g' "$output_file_path" ) ) 
then 
    echo "Sed Failure!"
    exit 1
fi

# Update app file using Python

python3 update_app_file.py  \
  "$output_file_path" \
  "k8s/app.yaml" \

# Deploy the app component 
kubectl apply -n $namesapce -f k8s/app.yaml

# Migration

# # Migrate
kubectl exec deploy/app-deployment -n $namesapce -- python manage.py migrate
# # Load fixtures
kubectl exec deploy/app-deployment -n $namesapce -- python manage.py loaddata demo.json

# Need to run a command in a pod
kubectl exec -it deploy/app-deployment -n $namesapce -- bash

# Get the public IP of the load balancer
kubectl get service app-service -n $namesapce

