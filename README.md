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
  - `--image`, the docker image to run the job
  - `--tag`, the docker image tag to run the job
  - `--schedule`, this is the cron schedule to run the job
  - `--environment` or `-e`, this is _optional_, the list of environment variables to set the job to run, pass it in the form `key=value`, for example `-e key=value1 -e key2=value2`
  - `--env-file`, _optional_, environment file, each line contains a line in the form `key=value` with the environment variables to pass to the process, use when you have repetitive environment variables between jobs.

- `edit`, edit a job, you _need to pass_ the job id (`--id`) and it will request the same arguments as `create` (if not passed as command line arguments)
- `delete`, removes a job, you need to pass the job id with `--id`, for example, `kron job delete --id 5` will remove job with id 5, it will ask you _yes/no_ before delete, pass `--yes` if you are sure you want to delete the job without any confirmation.

## How do I install Kron?

Kron is a Python 3 application, so first make sure you have python installed. You can install Kron using `pip`:

```sh
pip install kron
```

## Kron is failing with something regarding the server, what could be wrong?

You need to tell Kron where is your Kronbute server, by default is pointing to `localhost:8080`, if you want to test another server, you have two options:

 - Pass the parameter `--server` with the address for the server, for example `kron --server http://anotherserver.com job list`
 - Set the _environment variable_ `KRONBUTE_SERVER` with the address of the server

