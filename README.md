# Starfinder

## Explanation of this directory's contents:
  
  docker/

	Currently contains the web entrypoint script
	Later we'll add database utilities here as needed
  
  starfinder/

	Houses all container code, including the application MVC

  .env-example

	Currently empty
	Will hold any sensitive variables (such as API keys) to avoid displaying them in our version control
  
  .git_ignore

	Prevents select elements from being pushed to version control (such as the .env)
  
  docker-compose.*

	These files determine how the containers will be created.
	Currently we only use docker-compose.development, but later we will need to handle production, staging, and development environments differently.
  
  Dockerfile

	Loads up the new containers
	Sets /code as the work directory
	Installs all requirements
  
  Dockerfile.db_util

	Currently doesn't do much
	Later will be used for database backups
  
  Makefile

	Contains commands that can be used to modify the container via the virtual python environment
	Currently has commands to run & stop the containers
  
  requirements.txt

	Contains a list of requirements that are installed by the Dockerfile
	Currently this is just a spitballing of potential requirements
