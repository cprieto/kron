# Kron - Command line utility for Kronbute

This is the repository for Kron, a command line utility for Kronbute job manager.

## Why kron?

Well, when I was developing Kronbute, the automatic scheduled job manager for Healthcare.com ETL processes, I got stuck making the UI for the application, I am not really creative with UI development in Javascript and I had another two projects to work on at the same time, so I decided to throw away the current UI to develop it later and create a simple command line utility to handle Kronbute jobs, this is the product of that love.

## What can I do with Kron?

Basically everything Kronbute allows you to do:

- Create a job to run under a schedule in Kronbute
- List all available jobs in Kronbute
- Display details about a Kronbute job
- Edit or modify a Kronbute job
- Delete a Kronbute job

More functionality will be available soon together with Kronbute development.

## What commands are available?

In general, a Kron command looks like this:

```sh
kron <area> <verb> [options]
```

Where `<area>` is any of `job` or `runs`, depending on what area you want to work on, for example, `job` is for job related operations: `list`, `create`, `edit`, `delete` are _verbs_ for the `job` command. Some commands use specific options.

The available verbs for the area `job` are:

- `list`, list all current jobs in Kronbute, available options are
- `view [jobid]`, view details of a job with id `jobid` 
- `create`, create a new job, it will ask for the following options if not provided:

  - `--name`, the name of the job
  - `--timezone`, _optional_, the timezone name to run the job on, by default is UTC, timezones looks like "America/New_York"
  - `--image`, the docker image to run the job
  - `--tag`, the docker image tag to run the job
  - `--group` or `-g`, this is _optional_, the list of environment groups to use with this job
  - `--schedule`, this is the cron schedule to run the job
  - `--entrypoint`, the image entry point to execute, _optional_
  - `--alias`, an alias name to know the job, it must be _unique_, _optional_
  - `--environment` or `-e`, this is _optional_, the list of environment variables to set the job to run, pass it in the form `key=value`, for example `-e key=value1 -e key2=value2`
  - `--env-file`, _optional_, environment file, each line contains a line in the form `key=value` with the environment variables to pass to the process, use when you have repetitive environment variables between jobs.

- `edit`, edit a job, you _need to pass_ the job id (`--id`) and it will request the same arguments as `create` (if not passed as command line arguments)
- `delete`, removes a job, you need to pass the job id with `--id`, for example, `kron job delete --id 5` will remove job with id 5, it will ask you _yes/no_ before delete, pass `--yes` if you are sure you want to delete the job without any confirmation.

The available verbs for the area `group` are:

- `list`, list all existing environment groups
- `view [groupid]`, view an environment group details
- `create`, create an environment group
    - `--name`, unique name for the environent group, case sensitive
    - `--environment` or `-e`, the list of environment variables to set, _optional_
    - `--env-file`, environment file to load environment variables
- `edit [groupid]`, edit an existing environment group, same parameters as `create`
- `delete [groupid]`, delete an existing evironment group

## How do I install Kron?

Kron is a Python 3 application, so first make sure you have python installed. You can install Kron using `pip`:

```sh
pip install git+https://github.com/cprieto/kron.git
```

## How do I upgrade Kron?

Again, this is easy using Pip:

```sh
pip install --upgrade git+https://github.com/cprieto/kron.git
```

## Kron is failing with something regarding the server, what could be wrong?

You need to tell Kron where is your Kronbute server, by default is pointing to `localhost:8080`, if you want to test another server, you have two options:

 - Pass the parameter `--server` with the address for the server, for example `kron --server http://anotherserver.com job list`
 - Set the _environment variable_ `KRONBUTE_SERVER` with the address of the server

## How do I know what version am I running?

For this we have the noun `version`, this will display in a nice way the version of the tool and Kronbute server we are connecting to.

```sh
kron info
```

## Using an import file

Instead of creating or edit a job using the command line you can load one or all yoru values from a YAML file, an example of a job YAML file:

```yaml
name: Sample job
alias: sample_job
image: hc/data-integration-job:latest
schedule: '*/5 * * * *'
timezone: UTC
groups:
  - sample_group_1
  - sample_group_2
entrypoint: python3 main.py

environment:
  VARIABLE1: VALUE1
  VARIABLE2:
```

**Notice** the way we declare the image and tag, _there is no separate entry_ for image and tag but it is declared in the docker way, `image:tag`, as in the command line, if no `tag` is declared, the default `latest` is used.

Use the `--import` option when creating or editing a file with _an existing_ YAML file with the job definition (or partial job definition):

```
kron job create --import sample.yml
```

You can declare a partial file, only with the attributes you are insterested to use/edit and pass the rest from the command line, for example, you can use a file with the environment variables but pass the name from the command line.

The relevance order is _command line > yaml file_, it means, if you declare the name in the YAML file but as well pass it with the `--name` option, the option from the command line will have preference _over_ the YAML file name, this is a very flexible way to declare options for edit, for example.

**Remember** YAML files are very delicate with tabs and spaces, read more about YAML syntax at [this Wikipedia page](https://en.wikipedia.org/wiki/YAML)

**IMPORTANT** Currently there is a bug with the way we specify YAML and environment variables all together [see](https://www.pivotaltracker.com/story/show/160248865), so if you provide YAML and the environment variable parameter at the same time it will use _only_ the parameters from the command line.

## Export one job

Now we have the `export` verb for the `job` noun, we can export to standard output the details of a job so we can recreate that job, for example:

```
kron job export 1
```

Will export the data for the job 1 to the standard output, to save it into a file you can redirect the output to a file:

```
kron job export 1 > some_file.yml
```

You can use the alias name for the job or the id, it won't matter.

