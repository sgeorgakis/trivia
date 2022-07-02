# Description: 

This is a Python Web App for consuming data from [Trivia API](https://opentdb.com/api_config.php) and pushing to a Transifex Project via its [API](https://transifex.github.io/openapi/index.html)
It is based on [Tornado](https://www.tornadoweb.org/en/stable/) and Python 3.9 version

# Prerequsities:

You must have a Transifex account, an API Key and a Transifex project for this app to work.
You must pass both to the app as environmental variables.
 - API Key: `TRANSIFEX_API_KEY`
 - Project Id: `TRANSIFEX_PROJECT_ID`

For starting the app with multiple threads (production mode) you must also set the `ENVIRONMENT` environmental variable to `prod`.

# Run

## Docker run
 You can use Docker to build and deploy this app.
 Build the image using the ``docker build -t transifex/trivia`` command<br>
 and then `docker run -e TRANSIFEX_API_KEY=${TRANSIFEX_API_KEY} -e TRANSIFEX_PROJECT_ID=${TRANSIFEX_PROJECT_ID} transifex/trivia -p 8888:8888` to run it,<br>specifying the required env variables

## Poetry run
 You can use poetry to run the app using the following commands: `poetry install` to install the required dependencies and `poetry run http_server` to start the server

## Python run
 You can simply use `python3 server.py` to run the app. You must however use `poetry install` before, to install the required dependencies

# Usage

The API is exposed on `8888` port.<br>
There is a simple healthcheck endpoint to ensure that the app has started under the `/healthcheck` path using `GET` method.

The user can start a session in Trivia's API, so he/she can receive different questions with each request for the same categories.<br>
This can be done under the `/session/start` path using `POST` method.<br>
The user can also reset the session using the `/session/reset` path, again with `POST` method. If there is no session active, this request will result in a `Bad Request` Status code.<br>
Finally, the user can stop the session using the `/session/stop` path with `POST` method. This however may result in getting the same questions/answers again and not add new ones in the Transifex resource.

The first step is to retrieve the categories from Trivia using a `GET` request to `/categories` path.<br>
This will return a json encoded response with the categories ids and descriptions.

For requesting questions from Trivia's API, the user has to make a `POST` request using the `/questions` path.<br>
A required path parameter is `category` that is the id of the category the user wants to fetch questions. The user can include as many categories as he/she wants.<br>
By specifying the optional path parameter `amount` the user can control how many questions will be fetched for each category.

After that, the app will first check if there is a resource in Transifex for each category.<br>
If there is one, it will fetch all the uploaded questions, delete the resource and recreate it including all the old and new questions.

Since Transifex's API is asynchronous, this API assumes that each request to upload data will be completed successfully and no check if failed or not occurs.

# Notes

Transifex's API did not work as expected. According to the specs of the task, uploading a new file should replace all the previous resource strings with the new ones.<br>
I noticed, though, that the resource was left untouched. This is the reason I decided to fetch all the previous inserted resource strings, delete the resource and recreate it.<br>

As the number of resource strings is growing, so will the payload and we can probably end up with a `413` status code.