# starfinder

Currently erroring on `make run` with the following message:

	(llw) bash-3.2$ make run
	if [ ! -d "./database_data" ]; then mkdir -p ./database_data; fi
	environment:
	Removing starfinder_web_1
	starfinder_database_1 is up-to-date
	Starting starfinder_db_util_1 ...
	Starting starfinder_db_util_1
	Recreating 3838074e921a_starfinder_web_1 ...
	Recreating 3838074e921a_starfinder_web_1 ... error

	ERROR: for 3838074e921a_starfinder_web_1  Cannot start service web: OCI runtime create failed: container_linux.go:296: starting container process caused "exec: \"/code/web_entrypoint.sh\": permission denied": unknown

	ERROR: for web  Cannot start service web: OCI runtime create failed: container_linux.go:296: starting container process caused "exec: \"/code/web_entrypoint.sh\": permission denied": unknown
	ERROR: Encountered errors while bringing up the project.
	make: *** [run] Error 1