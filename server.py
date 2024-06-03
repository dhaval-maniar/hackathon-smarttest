import os
from output import run_the_script
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

app = App(token="xoxb-7197060453319-7205043179542-O2dfNPQdtaXjVUtTGwANdmyr")

# Add functionality here later
# @app.event("app_home_opened") etc.

@app.message(".*gerrit.eng.nutanix.com*")
# @app.message(".*")
def message_hello(message, say):
    print(message)
    say(f"Hey there <@{message['user']}>!\nI heard you say {message['text']}")
    result = run_the_script()
    say(result)

# Ready? Start your app!
if __name__ == "__main__":
    SocketModeHandler(app, "xapp-1-A076WDG0L6L-7211825570851-ee15bfc63bba471d0fc1c02a8dcc02c7453861852b2f6971a137c95ca380ac97").start()
