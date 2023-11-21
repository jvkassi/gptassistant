import requests
import json
import os


def create_tickets(args):

  redmine_api_key = os.environ['REDMINE_KEY']
  project_id = args["project_id"]
  ticket_title = args["ticket_title"]
  #ticket_priority = args["ticket_priority"]

  url = "https://projets.smile.ci/issues.json"

  payload = json.dumps({
      "issue": {
          "project_id": project_id,
          "subject": ticket_title,
          "priority_id": 4
      }
  })
  headers = {
      'Content-Type': 'application/json',
      'X-Redmine-API-Key': redmine_api_key
  }

  response = requests.request("POST", url, headers=headers, data=payload)

  print(response.text)
  return response.text
