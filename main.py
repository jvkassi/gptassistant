import glob
import importlib.util
import json
import os
import sys
import time

import openai

INSTRUCTIONS = """
You are a chatbot for linux system administrator
"""

TOOLS = {}

# Path to the directory containing your Python files
directory_path = 'tools'

# Iterate over each .py file in the directory
for file_path in glob.glob(os.path.join(directory_path, '*/*.py')):
  module_name = os.path.basename(file_path)[:-3]  # Remove '.py' from filename

  # Create a module spec
  spec = importlib.util.spec_from_file_location(module_name, file_path)
  module = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(module)

  # Add functions from the module to the hash
  for attr in dir(module):
    # Check if the attribute is a callable function and not a built-in
    if callable(getattr(module, attr)) and not attr.startswith("__"):
      TOOLS[attr] = getattr(module, attr)

print(TOOLS)

DESCRIPTIONS = []
for file_path in glob.glob(os.path.join(directory_path, '*/*.json')):
  with open(file_path, 'r') as file:
    print(file_path)
    tool = {"type": "function", "function": json.load(file)}
    DESCRIPTIONS.append(tool)

print(DESCRIPTIONS)


def setup_assistant(client, task):
  # create a new agent
  ASSISTANT_ID = "asst_8kdjntD69ZrjARS9nU6QYtNc"
  # assistant = client.beta.assistants.retrieve(ASSISTANT_ID)
  assistant = client.beta.assistants.update(ASSISTANT_ID,
                                            tools=DESCRIPTIONS,
                                            model="gpt-3.5-turbo")

  # assistant = client.beta.assistants.create(
  #     name="redmine",
  #     instructions=INSTRUCTIONS,
  #     tools=[{
  #         "type": "function",
  #         "function": {
  #             "name": "list_tickets",
  #             "description":
  #             "Use this function to list the last opened tickets of redmine.",
  #             "parameters": {
  #                 "type": "object",
  #                 "properties": {
  #                     "numbers_of_tickets": {
  #                         "type": "integer",
  #                         "description": "The number of last tickets to get",
  #                     },
  #                 },
  #                 "required": ["numbers_of_tickets"]
  #             },
  #         },
  #     }],
  #     # model="gpt-4-1106-preview",
  #     model="gpt-3.5-turbo")

  # Create a new thread
  thread = client.beta.threads.create()

  # Create a new thread message with the provided task
  client.beta.threads.messages.create(
      thread.id,
      role="user",
      content=task,
  )

  # Return the assistant ID and thread ID
  return assistant.id, thread.id
  
def add_message(client, thread_id, message):

  thread_message = client.beta.threads.messages.create(
  thread_id,
  role="user",
  content=message)

  return thread_message

def run_assistant(client, assistant_id, thread_id):
  # Create a new run for the given thread and assistant
  run = client.beta.threads.runs.create(thread_id=thread_id,
                                        assistant_id=assistant_id)

  # Loop until the run status is either "completed" or "requires_action"
  while run.status == "in_progress" or run.status == "queued":
    time.sleep(1)
    run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

    # At this point, the status is either "completed" or "requires_action"
    if run.status == "completed":
      return client.beta.threads.messages.list(thread_id=thread_id)
    if run.status == "requires_action":
      tool_call = run.required_action.submit_tool_outputs.tool_calls[0]
      print(tool_call.function.name)
      arguments = json.loads(tool_call.function.arguments)
      print(arguments)
      # prompt = json.loads(tool_call.function.arguments)['prompt']
      # image_url = generate_image(prompt)
      # tool = TOOLS[tool_call.function.name]
      tool = TOOLS[tool_call.function.name]
      result = tool(arguments)
      run = client.beta.threads.runs.submit_tool_outputs(
          thread_id=thread_id,
          run_id=run.id,
          tool_outputs=[
              {
                  "tool_call_id":
                  run.required_action.submit_tool_outputs.tool_calls[0].id,
                  "output":
                  result,
              },
          ])


if __name__ == "__main__":
  if len(sys.argv) == 2:
    client = openai.OpenAI()
    task = sys.argv[1]
    assistant_id, thread_id = setup_assistant(client, task)
    print(
        f"Debugging: Useful for checking the generated agent in the playground. https://platform.openai.com/playground?mode=assistant&assistant={assistant_id}"
    )
    print(
        f"Debugging: Useful for checking logs. https://platform.openai.com/playground?thread={thread_id}"
    )

    # while True:

    #   script = input("enter your message ")
    #   id = add_message(client, thread_id, script)
    #   print(id)
    #   messages = run_assistant(client, assistant_id, thread_id)
    #   message_dict = json.loads(messages.model_dump_json())
    #   print(message_dict['data'][0]['content'][0]["text"]["value"])

    messages = run_assistant(client, assistant_id, thread_id)

    message_dict = json.loads(messages.model_dump_json())
    print(message_dict['data'][0]['content'][0]["text"]["value"])

  else:
    print("Usage: python script.py <message>")
    sys.exit(1)
