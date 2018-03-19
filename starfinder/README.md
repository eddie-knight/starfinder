# ~/starfinder/

## Explanation of this directory's contents:

  app/
    Houses all controllers

  db/ 
    Houses all models

  templates/
    Houses all elements for building views

  __init__.py
  	Initializes this directory's contents for use as python modules

  config.py
    Config() object that allows for communication with .env

  exception.py
    Houses various exception methods for our app

  logging.py
    Enables log.DEBUG(), log.WARNING(), log.INFO(), log.ERROR(), log.CRITICAL()
    Parameters inserted in one of the above will be displayed via:
    docker logs -f starfinder_web_1

  starfinder_app.py
    Effective start point for application code