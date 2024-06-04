import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from test import caller
 
app = App(token=os.getenv("SLACK_BOT_TOKEN"))
 
# Add functionality here later
# @app.event("app_home_opened") etc.
 
@app.message(".*gerrit.eng.nutanix.com*")
def message_hello(message, say):
    # print(message)
    # say(f"Hey there <@{message['user']}>!\nI heard you say {message['text']}")
    # result = run_the_script()
    # oid = "665cac7c2bc0c413c8fae9b2"
    result = caller()
    # time.sleep(1)
    say(next(result))
    # time.sleep(1)
    say(next(result))
    result_json = next(result)
    message = f"Failed: {result_json['failed']}\nPassed: {result_json['passed']}\n"
    for x in result_json['failed_test_cases']:
        message += f"Failed Test Case: {x['name']}\nLog: {x['url']}\n------------------\n"
    say(message)
 
# Ready? Start your app!
if __name__ == "__main__":
    SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN")).start()