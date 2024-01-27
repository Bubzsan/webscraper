# Web scraping

This will basically be used to harvest some data from the webpage and put it into an excel sheet.

# Usage

Pass the "search power" as an environment variable. This controls how much the script will run for.
For example, with the power set to 50, it takes around 2 minutes for the script to run. The more it runs, more research it will do in the website.

Run with:

```shell
docker run --name scraper -e "SEARCH_POWER=50" bbarros/webscraper:latest
```

After execution the file will be generated inside of the container. Copy it over with

```shell
docker cp "awesome_rhodes:/usr/src/app/metaculus_sample.xlsx" "./metaculus_sample2.xlsx"
```

# Docker (development)

Build with:

```shell
docker build -t bbarros/webscraper:latest .
```

Push to DockerHub
```
docker push bbarros/webscraper:latest 
```

Check out the registry at https://hub.docker.com/repository/docker/bbarros/webscraper/general

To test locally change the entrypoint to be the shell instead of the script. 

Then run with:

```shell
docker run --name my-web-scraper -v "$(pwd)":/usr/src/app -it --user="$(id -u):$(id -g)" web-scraper
```

When inside the docker image:

```python
python web_scraper.py
```
