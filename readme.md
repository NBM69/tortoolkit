# TK - A Telegram Bot

## Notes:
Needs to be rebased to newer v0.2.4 beta.
Working an a different deployment strategy (Docker Image).

## Deploy via Heroku
- Fork this repository
- Before deploying, you should change the configs. 
- Tortoolkit > Consts > ExecVarsSample.py

Note: you can also click the deploy button & add the variables manually.

<p><a href="https://heroku.com/deploy?template=https://github.com/reaitten/ttk"> <img src="https://img.shields.io/badge/Deploy%20To%20Heroku-blueviolet?style=for-the-badge&logo=heroku" width="200""/></a></p>

# Credits

> [tortoolkit's TorToolkit-Telegram](https://github.com/tortoolkit/TorToolkit-Telegram)

> [sahadz's TorToolkit-Telegram](https://github.com/sahadz/TorToolkit-Telegram)

## Variables
`IS_VPS` = False
## Compulsory Vars

`API_HASH` = Obtained from Telegram 

`API_ID` = Obtained from Telegram

`BOT_TOKEN` = Obtained from Botfather

`BASE_URL_OF_BOT` = IP/domain of your bot like "https://appname.herokuapp.com" (for heroku)

`ALD_USR` = It is a list of IDs of all the allowed groups and useres who can use this bot in private.

`DB_URI` = Postgres database URL.

## Optional Vars
(IT IS RECOMMENDED TO SET THE OPTIONAL VARS FROM SETTINGS MENU, If not all vars atleast use settings menu for RCLONE that way is much easier.)

`EDIT_SLEEP_SECS` = Seconds to Sleep before edits. Recommended is 40.

`TG_UP_LIMIT` = Telegram Upload limit in bytes.

`FORCE_DOCUMENTS` = Should all the upload to telegram be made as documents or not.

`COMPLETED_STR` = Character used to denote completed progress. 

`REMAINING_STR` = Character used to denote remaining progress.

`RCLONE_BASE_DIR` = Rclone Base Directory to where stuff should be clonned. (cannot be configured from settings)

`LEECH_ENABLED` = Upload to telegram should be enabled or not.

`RCLONE_ENABLED` = Upload to rclone should be enabled or not.

`DEFAULT_TIMEOUT` = Default destination to choose if the user fails to choose upload destination in 60 seconds.

`RCLONE_CONFIG` = Rclone file path.

`DEF_RCLONE_DRIVE` = Default Rclone drive from the config file.

`MAX_YTPLAYLIST_SIZE` = Max size of a playlist that is allowed (Number of videos)

`MAX_TORRENT_SIZE` = Max torrent size in GBs

Other varibles are not to be changed.
## Commands
add in [@BotFather](https://t.me/BotFather)

    leech - To Leech a torrent or download a direct link
    ytdl - Donwload YouTube Video
    pytdl - Download YouTube Playlist
    about - About the bot
    status - Status of all the downloads
    server - Get server status
    usettings - User Settings
    settings - Settings of the bot ⚠️ Admin Only
    pauseall - Pause all torrents⚠️ Admin Only
    resumeall - Resume all torrents⚠️ Admin Only
    purge - Delete all torrents ⚠️ Admin Only
    getlogs - Get the robot logs ⚠️ Admin Only
