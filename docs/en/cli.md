<div class="hero-section">
  <h1><i class="fas fa-hexagon" style="margin-right: 0.5rem;"></i>Using the OpenHEXA CLI</h1>
</div>
</div>

OpenHEXA comes with a CLI you can install globally on your system. This CLI allows you to interact with the OpenHEXA API and perform various tasks such as creating and managing pipelines, running local jobs and more.

## Installation
To install the CLI, you have to have `Python >3.9` and `pip` installed on your system. Then you can install the CLI using the following command:

```bash
python -m pip install openhexa.sdk
```

You can then run the CLI using the `openhexa` command.
```bash
openhexa --help
```

## Configuration
By default, the CLI will look for a configuration file in `~/.openhexa.ini`. You can interact with the configuration using the `openhexa config` command.
The CLI comes pre-configured to use `https://api.openhexa.org` as the API endpoint. You can change this by running:

```bash
openhexa config set_url <my-endpoint-url>
```

In case you need more information about the CLI, you can use the `--help` flag to get more information about the commands and their options.

```bash
openhexa --help
openhexa workspaces --help
openhexa pipelines init --help
```

In case you are presented with SSL verification errors, you can disable SSL verification (activated by default) with the following setting:

```bash
export HEXA_VERIFY_SSL=false
```

Note that you should use this only when really necessary to interact with local installations of OpenHEXA. It may be required for example when we're lacking the full chain in the SSL certificate.

## Managing workspaces
The CLI needs to be configured with the workspaces you want to interact with. You can add, remove and list workspaces using the `openhexa workspaces` command.

### Adding a workspace
To add a workspace to the configuration, you can run:

```bash
openhexa workspaces add <workspace-slug>
```

The CLI will ask you to provide the API key needed for this workspace. This API key can be found in the OpenHEXA web interface on the pipelines page. The newly added workspace will be set as the active workspace.

Note: The CLI needs a valid API key per workspace.

### Activating a workspace
You can activate a workspace using the `openhexa workspaces activate <workspace-slug>` command. This will set the active workspace for the CLI. All other CLI commands will use this workspace as the default. You can see the list of added workspaces using the `openhexa workspaces list` command.

## Pipelines
You can list, create, update, download, run and delete pipelines using the `openhexa pipelines` command.

### Listing pipelines
You can list the pipelines in the active workspace using the `openhexa pipelines list` command.

### Creating a pipeline
You can create a pipeline using the `openhexa pipelines init <pipeline-name>` command. This will create a new directory with the pipeline name and a `pipeline.py` file. You can then edit this file to define your pipeline. You can then run the pipeline using the `openhexa pipelines run <pipeline-name>` command.

The recommended approach is to have a pipeline per git repository. This allows you to version control your pipeline and share it with others. At the creation of the pipeline, the CLI will ask you if you want to create a github workflow to push your pipeline to OpenHEXA automatically based on a git tag, a push to
`main` or a manual action via the GitHub UI.

When pushing a pipeline, you can optionally specify:
- **Functional type** using `-ft` or `--functional-type`: Categorize your pipeline as `extraction`, `transformation`, `loading`, or `computation`
- **Tags** using `-t` or `--tag`: Add multiple tags to organize and filter pipelines (can be used multiple times)

Example:
```bash
openhexa pipelines push ./my-pipeline -ft extraction -t data-quality -t covid19
```


### Running a pipeline
Pipelines can be run locally using [Docker](https://www.docker.com/products/docker-desktop/). Docker must be installed on your system to run pipelines.

You can run a pipeline using the `openhexa pipelines run <pipeline-path>` command. If your pipeline requires any parameters, you can pass them using a config file or directly as a json string.

As a JSON string:
```bash
openhexa pipelines run <pipeline-path> -c '{"param1": "value1", "param2": "value2"}'
```

As a config file:
```bash
echo '{"param1": "value1", "param2": "value2"}' > ./config.json
openhexa pipelines run <pipeline-path> -f ./config.json
```

If you want your pipeline to run with a different image than the default one (`blsq/openhexa-blsq-environment:latest`), you can use the `--image` flag to specify the image to use.

```bash
openhexa pipelines run <pipeline-path> --image <image-name>
```

### Updating a pipeline
You can update a pipeline using the `openhexa pipelines push <pipeline-path>` command. This will update the pipeline in the OpenHEXA API with the new pipeline definition.

The `push` command supports several options:
- `-c, --code`: Specify the pipeline code to update
- `-n, --name`: Set the version name
- `-d, --description`: Add a version description
- `-l, --link`: Provide a link to the version commit
- `-ft, --functional-type`: Set the functional type (`extraction`, `transformation`, `loading`, or `computation`)
- `-t, --tag`: Add tags (can be used multiple times for multiple tags)
- `--yes`: Skip confirmation prompts (useful for CI/CD)

### Download a pipeline
You can download a pipeline using the `openhexa pipelines download <pipeline-slug> <path>` command. This will download the pipeline to the `path` given. If the path is not empty, the CLI will ask you if you want to overwrite the existing files.

### Deleting a pipeline
You can delete a pipeline using the `openhexa pipelines delete <pipeline-slug>` command. This will delete the pipeline from the OpenHEXA API.


## FAQs
### How do I get the API key for a workspace?
You can find the API key for a workspace in the OpenHEXA web interface on the pipelines page by clicking on "+". You need to be at least an editor of the workspace. The API key is a secret and should be kept safe. The CLI will ask you to provide the API key when adding a workspace.

### How do I get the workspace slug?
You can find the workspace slug in the OpenHEXA web interface on the pipelines page. The workspace slug is the part of the URL after `https://app.openhexa.com/workspaces/<workspace-slug>/`.

### How do I get the pipeline slug?
You can find the pipeline slug in the OpenHEXA web interface on each pipeline page.

### I'm getting SSL errors when trying to add a workspace.
You can [disable SSL verification](#configuration) if needed to interact with the server.