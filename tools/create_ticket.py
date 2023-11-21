import requests
import json
import os


def list_tickets(args):

  nb_tickets = args["numbers_of_tickets"]
  redmine_api_key = os.environ['REDMINE_KEY']
  url = "https://projets.smile.ci/issues.json?status_id=open&limit=" + str(
      nb_tickets)
  payload = {}
  headers = {
      'Content-Type': 'application/json',
      'X-Redmine-API-Key': redmine_api_key
  }

  response = requests.request("GET", url, headers=headers, data=payload)
  print(response.text)
  return response.text

