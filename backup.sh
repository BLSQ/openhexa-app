#!/bin/bash

# Fetch AWS credentials from environment variables
AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION}

# Fetch GCP credentials from a JSON file
GCP_CREDENTIALS_FILE=${GCP_CREDENTIALS_FILE}

# Set the GCP credentials
export GOOGLE_APPLICATION_CREDENTIALS=${GCP_CREDENTIALS_FILE}

if ! command -v gcloud &> /dev/null
then
    echo "gcloud CLI could not be found. Please install it first."
    exit 1
fi
if ! command -v aws &> /dev/null
then
    echo "aws CLI could not be found. Please install it first."
    exit 1
fi

# List GCP buckets and sync each to S3
for bucket in $(gcloud storage ls | grep hexa-demo | sed 's|gs://||; s|/$||'); do
    echo "Syncing bucket ${bucket}"
    # Create S3 bucket if it doesn't exist
    bucket_backup=${bucket//[^a-zA-Z0-9.\-_]/}
    echo "Creating S3 bucket ${bucket_backup}"
    aws s3api create-bucket --bucket ${bucket_backup} --region ${AWS_DEFAULT_REGION} --create-bucket-configuration LocationConstraint=${AWS_DEFAULT_REGION} || true
    gcloud storage rsync gs://${bucket} s3://${bucket} --recursive
    # Another option is to use Transfer Service : issue - IAM permission for transfer on GCP i think
    # gcloud transfer jobs create gs://${bucket} s3://${bucket}
    break
done

echo "Synchronization complete."

echo "Try dump database"

# ./cloud-sql-proxy blsq-dip-test:europe-west1:hexa-sirius
# Need to run the proxy through cloud

# PG Dump All
# pg_dumpall -h 127.0.0.1 -p 5432 -l hexa-app-demo -U hexa-app-demo> pg_dumpall.sql

# PG Dump
# pg_dump -h 127.0.0.1 -p 5432 -d alkulk5zu8tmpimk -U alkulk5zu8tmpimk> pg_dump.sql

# SQL Export -> need to use service account
# gcloud sql export sql hexa-sirius gs://hexa-app-demo-backup/pg_dump_all.sql --database hexa-app-demo
