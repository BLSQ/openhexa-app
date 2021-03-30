import sys
import yaml

terraform_output_file_path = sys.argv[1]
config_file_path = sys.argv[2]
HEXA_APP_IMAGE = "blsq/openhexa-app:latest"


print(f"Config Map using Terraform output")

# Open & load the terraform output file to fetch relevant project config values
with open(terraform_output_file_path, "r") as terraform_output_file:
    terraform_output = yaml.load(terraform_output_file, Loader=yaml.FullLoader)

    # Open and load the project config file and update it with the values from the terraform output
    with open(config_file_path, "r+") as project_config_file:
        config = list(yaml.load_all(project_config_file, Loader=yaml.FullLoader))
        config[0]["data"]["ALLOWED_HOSTS"] = terraform_output.get("hexa_domain")
        config[1]["spec"]["template"]["spec"]["nodeSelector"][
            "cloud.google.com/gke-nodepool"
        ] = terraform_output.get("NODE_POOL_SELECTOR")
        config[1]["spec"]["template"]["spec"]["containers"][0]["image"] = HEXA_APP_IMAGE
        config[1]["spec"]["template"]["spec"]["containers"][0]["readinessProbe"][
            "httpGet"
        ]["httpHeaders"][0]["value"] = terraform_output.get("hexa_domain")
        config[1]["spec"]["template"]["spec"]["containers"][1]["command"][
            2
        ] = f"-instances=\"{terraform_output.get('CLOUDSQL_CONNECTION_STRING')}\"=tcp:5432"
        config[2]["spec"]["domains"][0] = terraform_output.get("hexa_domain")
        config[4]["metadata"]["annotations"][
            "kubernetes.io/ingress.global-static-ip-name"
        ] = terraform_output.get("gcp_global_address")

        # Write back the updated file data to disk
        # (We need to truncate the file first, as we want to overwrite its content with the updated config)
        project_config_file.seek(0)
        project_config_file.truncate()
        project_config_file.write(
            yaml.dump_all(
                config,
                default_flow_style=False,
                sort_keys=False,
            )
        )

        print("Successfully extracted terraform output and updated app.yaml")
