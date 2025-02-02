# stb

A universal tool for local microservice management

## Installation

```bash
pipx install stb-mnt
```

## Usage

### Setup

* To download and setup backend/service1 microservice as a subdirectory to the current working directory, use:

```bash
stb setup backend/service1
```

* To download and setup backend/service1 and backend/service2 as subdirectories to current working directory, use:

```bash
stb setup backend/service1 backend/service2
```

* To setup backend/service1 that you have already cloned, use:

```bash
stb setup backend/service1 --no-clone
```

Note that if you want to clone repositories, you must first set a `git_url` using `stb config set git_url` command

### Update

* To update .env file in accordance with .env.example in a microservice:

```bash
stb update env
```

* To synchronize service ports between all installed microservices (you can specify which ones will run locally with the `--local` option):

```bash
stb update ports
```

* To install the dependencies from poetry.lock file and update submodules:

```bash
stb update package
```

* To update poetry.lock file, install dependencies, update submodules, stash current changes, checkout to master, pull from remote, and recreate databases:

```bash
stb update package -pucd
```

or  

```bash
stb update package --pull --update --checkout --reset-databases
```

### DB

* To upgrade migrations in a microservice:

```bash
stb db ugrade
```

* To create databases and upgrade its migrations in a microservice:

```bash
stb db create
```

* To drop databases in a microservice:

```bash
stb db drop
```

* To drop and recreate databases, and upgrade migrations in a microservice:

```bash
stb db reset
```

* To upgrade migrations in parallel for faster upgrades (useful for large monoliths with multiple databases), you can use the -p (--parallel) option:

```bash
stb db create -p
```
  
```bash
stb db reset -p
```
  
* To force dropping of databases in case another program is using them at the same time, you can use the -f (--force) option:

```bash
stb db drop -f
```
  
```bash
stb db reset -f
```
  
### Use

`stb use` allows you to take a company private package and install either a cloud version or a local version of it. STB will preserve all extras and will gracefully handle any issues that might happen while updating.

* To install a local version of `my_package` that is located at `../my_package`:

```bash
stb use my_package ../my_package
```

* To install a cloud version of `my_package` with tag `8.3.1`:

```bash
stb use my_package 8.3.1
```

### Run

* To update and run the select services concurrently:

```bash
stb run service1 service2
```

### Config

* To set a git url for cloning:

```bash
stb config set git_url git@github.com:mycompany
```

### How directories are selected for update/db

For every update, you can specify:

1) A microservice directory, which will cause stb to update only that microservice
2) Several microservice directories, which will cause stb to update these microservices and integrate them together (for example, `update ports` assigns ports to local microservices and updates their links in other microservices to match the assigned ports)
3) A directory with multiple microservice subdirectories inside it, which is equivalent to (2) with the list of subdirectories as arguments
4) Nothing, which will choose the current working directory as the first argument and will be equivalent to (1) or (3)
