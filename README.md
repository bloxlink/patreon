<div align="center">
    <img src="https://cdn.discordapp.com/attachments/480614508633522176/548713249982382091/BloxlinkLogoNew.png" height="200" width="200">
    <h2>Bloxlink</h2>
    <p align="center">
        <p>Roblox Verification made easy! Features everything you need to integrate your Discord server with Roblox.</p>
        <p><a href="https://blox.link">
            <b>View website » </b>
        </a> </b> </p>	
        <p> <a href="https://blox.link/invite">
            <b>Invite Bloxlink »</b>
        </a> </p>
        <p> <a href="https://blox.link/support">
            <b>Ask for support »</b>
        </a> </p>
    </p>
</div>
<p align="center">
    <a href="https://blox.link">
        <img src="https://img.shields.io/website-up-down-green-red/https/blox.link.svg?label=website">
    </a>
    <a href="https://discord.gg/jJKWpsr">
        <img src="https://img.shields.io/discord/372036754078826496.svg">
    </a>
</p>


### Contents
* [Packages](#packages)
* [Configuration](#configuration)
* [Basic Installation](#basic-installation)
* [License](#license)

------------------
#### Packages
This package relies on the following dependencies:
* [Docker](https://www.docker.com/)
* [rethinkdb](https://rethinkdb.com)
* [other package dependencies](https://github.com/bloxlink/patreon/blob/master/requirements.txt)

------------------
#### Configuration
This package relies on a [configuration file](https://github.com/bloxlink/patreon/blob/master/config.py) in order to load the appropriate settings. You can also import settings with environmental variables.

------------------
#### Basic Installation
```
$ git clone https://github.com/bloxlink/patreon
$ cd patreon
$ docker build -t patreon .
$ docker run patreon
```

NOTE: it's recommended you run this on a CRON job as the script will only __execute once__.

------------------
#### License
This repository has been released under the [MIT License](LICENSE).

------------------
Project maintained by [justin](https://github.com/tigerism).
Contact me on Discord: justin#1337
