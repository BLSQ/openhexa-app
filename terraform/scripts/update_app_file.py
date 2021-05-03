import sys
import yaml
import json

from pathlib import Path

terraform_output_file_path = Path(__file__).parent / Path("../output.json")

config_file_path = sys.argv[1]
hexa_app_image = sys.argv[2]

print(f"Config Map using Terraform output")

# Open & load the terraform output file to fetch relevant project config values
with open(terraform_output_file_path, "r") as terraform_output_file:
    terraform_output = json.load(terraform_output_file)

    # Open and load the project config file and update it with the values from the terraform output
    with open(config_file_path, "r+") as project_config_file:
        config = list(yaml.load_all(project_config_file, Loader=yaml.FullLoader))
        config[0]["data"]["ALLOWED_HOSTS"] = terraform_output[
            "aws_route53_record_name"
        ]["value"]
        config[1]["spec"]["template"]["spec"]["nodeSelector"][
            "cloud.google.com/gke-nodepool"
        ] = terraform_output.get("gcp_gke_default_node_pool_name")
        config[1]["spec"]["template"]["spec"]["containers"][0]["image"] = hexa_app_image
        config[1]["spec"]["template"]["spec"]["containers"][0]["readinessProbe"][
            "httpGet"
        ]["httpHeaders"][0]["value"] = terraform_output["aws_route53_record_name"][
            "value"
        ]
        config[1]["spec"]["template"]["spec"]["containers"][1]["command"][
            2
        ] = f"-instances={terraform_output['gcp_sql_instance_connection_name']['value']}=tcp:5432"
        config[2]["spec"]["domains"][0] = terraform_output["aws_route53_record_name"][
            "value"
        ]
        config[4]["metadata"]["annotations"][
            "kubernetes.io/ingress.global-static-ip-name"
        ] = terraform_output["gcp_global_address"]["value"]

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
