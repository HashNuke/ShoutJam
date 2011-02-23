ShoutJam
==========

This repo contains the source code for a small-scale SMS social network that I operated in Feb 2009 for around 3 weeks after which I had to shutdown due to compelling reasons.

__*s60_server.py*__ : is a python script that should on the Symbian S60 2nd edition phones. I developed and used it on my Nokia N70, which is a Symbian S60 2nd edition FeaturePack-3 phone. You'll need a PyS60 (which is Python for Symbian S60) on the phone to run this.

__*shoutjam.py*__ : is the python script that should be run on your PC. You'll need SQLite3 to run this.

The PC communicates with the Symbian phone via bluetooth. My nokia phone did not have an open protocol to communicate via USB so I had to write a Bluetooth one. That is also the reason why (if you dig into the source  will understand) that a secret command can be set, which when sent, will return the registered user count along with the battery level of the phone (yes you can always put it on charge and leave it that way).

Database details and other setup details coming soon...


Story
------

Everyone has their share of adventures in life. This was one of my best. But the story is for another time, which I'll post it soon (It's just a small but a memorable adventure).
