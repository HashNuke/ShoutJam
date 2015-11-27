ShoutJam
==========

Source code for an SMS social network that I operated in Feb 2009 for around 3 weeks after which I had to shutdown due to compelling reasons.

* **s60_server.py** : python script to run on any Symbian S60 2nd edition phone. Mine was a Nokia N70 (S60 2nd edition FeaturePack-3). You'll need *Python for Symbian S60* (PyS60) on the phone to run this.

* **shoutjam.py** : python script to run on a Linux computer. Requires SQLite3.

Computer communicates with the phone via bluetooth. My Nokia phone did not have an open protocol to communicate via USB. So I had to do it over Bluetooth.

A secret SMS command can be set to get back registered user count and the battery level of the phone (yes you can always put it on charge and leave it that way).

Database details and other setup details coming someday...
