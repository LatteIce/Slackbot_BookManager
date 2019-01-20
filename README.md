# Slackbot_BookManager
Python bot to manage owning books in Slack. Comments are written in Japanese.

## Required libraly
Below python libraries are required for running this bot.
* slackbot
* requests
* sqlite3

## Command list

<dl>
  <dt>create database</dt>
  <dd>MUST RUN THIS COMMAND FIRST. create a new SQLite database file to store data.</dd>
  <dt>add [ISBN number]</dt>
  <dd>add the book to your bookshelf (means the book list you have owned)</dd>
  <dt>check [ISBN number]</dt>
  <dd>reply whether you have owned the book.</dd>
  <dt>show</dt>
  <dd>reply your bookshelf list.</dd>
</dl>

## Usage
* Open "slackbot_settings.py" and change "API_TOKEN"'s value to yours.
* run "run.py" then the bot might be up on Slack.
* Send above command to the bot as a massage then it work.

and...you can add a new wonderful function to your bot with modifying bookmanager.py!
