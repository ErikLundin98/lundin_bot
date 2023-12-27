# Setting up the bot as a service

* Edit the `voice_assistant.service` file so that the path to the voice assistant matches your setup
* Then, run the following:
  * sudo systemctl daemon-reload
  * sudo systemctl enable voice_assistant.service
  * sudo systemctl start voice_assistant.service

* All done! You can verify that everything started correctly by checking `systemctl status voice_assistant.service`
