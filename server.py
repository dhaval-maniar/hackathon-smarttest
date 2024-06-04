import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from script import run_the_script

# Initialize the Slack App with the bot token
slack_app = App(token=os.getenv("SLACK_BOT_TOKEN"))

# Define a message handler for messages containing "gerrit.eng.nutanix.com"
@slack_app.message(".*gerrit.eng.nutanix.com*")
def handle_message(message, say):
    # Run the script and get the result
    script_result = run_the_script(message['text'])

    # Send the first two status_updates as messages
    say(next(script_result))
    say(next(script_result))

    # Get the JSON result from the script
    result_json = next(script_result)

    # Format a message with the failed and passed test cases
    message_text = f"Failed: {result_json['failed']}\nPassed: {result_json['passed']}\n"
    for test_case in result_json['failed_test_cases']:
        message_text += f"Failed Test Case: {test_case['name']}\nLog: {test_case['url']}\n------------------\n"

    # Send the formatted message with the urls
    say(message_text)

# Start the Slack App in Socket Mode
if __name__ == "__main__":
    SocketModeHandler(slack_app, os.getenv("SLACK_APP_TOKEN")).start()