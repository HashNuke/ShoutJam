from pysqlite2 import dbapi2 as sqlite
from bluetooth import *
import string, re, demjson
from time import gmtime, strftime

notsent=0
sockstatus="first"

# change this control number. Used to manage service via SMS

controlNumber = "+91xxxxxxxxxx"

# number for the shoutjam service
shoutJamNumber = "xxxxxxxxxx"

# path to the sqlite database
databasePath = "shoutjam.db"

connection = sqlite.connect(databasePath, isolation_level=None)
cursor = connection.cursor()
cursor2 = connection.cursor()
cursor3 = connection.cursor()

# Bluetooth MAC address of the phone. I called it server coz it serves the SMSes :)
server_address = "xx:xx:xx:xx:xx:xx"

# The port where it's listening
port = 4

print "Starting..."    

while(1):
    conntest=0
    while(conntest!=1):
        try:
            if(sockstatus!="first"):
                sock.close()
            sock = BluetoothSocket( RFCOMM )
            sock.connect((server_address, port))    
            conntest=1
            sockstatus=""
        except:
            conntest=0
    while(1):    
        if(notsent!=1):
            cursor.execute('SELECT id,msg,phone FROM psq LIMIT 5')
            pushdata = []
            for each_ps in cursor:
                theid = str(each_ps[0])
                thenum = each_ps[2]
                themsg = each_ps[1]
                each_data = {'msg': themsg, 'to': str(thenum)}
                cursor2.execute('DELETE FROM psq WHERE id = ?', (theid,))
                pushdata.append(each_data)
        outputJSON = demjson.encode({'payload': pushdata })
        try:
            sock.send(outputJSON)
        except:
            notsent=1
            print "Send error"
        try:
            pulldata = sock.recv(4096)
        except:
            break

        pulldata = demjson.decode(pulldata)
        if(pulldata['payload']!=[]):
            for one_pull in pulldata['payload']:
                thesender = one_pull['sender']
                msg_cnt = one_pull['msg']
                print thesender+" "+msg_cnt

                #calculate parameters from msg
                if(re.compile("@all ", re.IGNORECASE).match(msg_cnt)!=None or re.compile("@all\n", re.IGNORECASE).match(msg_cnt)!=None):
                    the_act_msg = string.split(msg_cnt," ")
                    del the_act_msg[0]
                    the_act_msg = string.join(the_act_msg)
                    timenow = strftime("%a, %d %b %Y %H:%M:%S", gmtime())
                    cursor.execute('SELECT * FROM users WHERE phone = ?',(thesender,))
                    try:
                        thenick = cursor.fetchone()[1]
                        if(thenick[0:4]=="num:"):
                            theerror_msg = "You must join ShoutJam using the\n@join <username>\ncommand before sending messages to others"
                            cursor.execute('INSERT INTO psq("msg","phone") VALUES(?,?)', (theerror_msg,thesender,))
                            continue;
                        cursor.execute('INSERT INTO statuses("nick","msg","dated") VALUES(?,?,?)', (thenick, the_act_msg, timenow,))
                        cursor.execute('SELECT phone FROM followers JOIN users ON (followers.follower=users.nick) WHERE following = ? AND service="start" ', (thenick,))
                        msgtosend = "@"+thenick+": "+the_act_msg
                        for row in cursor:
                            cursor2.execute('INSERT INTO psq("phone", "msg") VALUES(?,?)', (row[0],msgtosend,))
                    except:
                        print " "
                elif(re.compile("@del", re.IGNORECASE).match(msg_cnt)!=None):
                    the_nickname = string.split(msg_cnt," ")
                    the_nickname = the_nickname[1]
                    if(thesender==controlNumber):
                        cursor.execute('DELETE FROM users WHERE nick = ?',(the_nickname,))
                        cursor.execute('DELETE FROM followers WHERE follower = ? AND following = ?',(the_nickname,the_nickname,))
                elif(re.compile("@ann", re.IGNORECASE).match(msg_cnt)!=None):
                    if(thesender==controlNumber):
                        the_act_msg = string.split(msg_cnt," ")
                        del the_act_msg[0]
                        the_act_msg = string.join(the_act_msg)
                        timenow = strftime("%a, %d %b %Y %H:%M:%S", gmtime())
                        cursor.execute('SELECT * FROM users WHERE phone = ?',(thesender,))
                        try:
                            thenick = cursor.fetchone()[1]
                            cursor.execute('INSERT INTO statuses("nick","msg","dated") VALUES(?,?,?)', (thenick, the_act_msg, timenow,))
                            cursor.execute('SELECT phone FROM users')
                            msgtosend = "@"+thenick+": "+the_act_msg
                            for row in cursor:
                                cursor2.execute('INSERT INTO psq("phone", "msg") VALUES(?,?)', (row[0],msgtosend,))
                        except:
                            print " "
                elif(re.compile("@add ", re.IGNORECASE).match(msg_cnt)!=None):
                    the_nickname = string.split(msg_cnt," ")
                    the_nickname = the_nickname[1]
                    fullnum = "+91"+the_nickname
                    numstr = "num:"+the_nickname
                    if(len(the_nickname)!=10):
                        print the_nickname+" isn't 10 chars"
                    else:
                        try:
                            the_add_num = int(the_nickname)
                            cursor.execute('SELECT nick FROM users WHERE phone = ?',(thesender,))
                            try:
                                thesendernick = cursor.fetchone()[0]
                                if(thesendernick[0:4]=="num:"):
                                    theerror_msg = "You must join ShoutJam using the\n@join <username>\ncommand before sending messages to others"
                                    cursor.execute('INSERT INTO psq("msg","phone") VALUES(?,?)', (theerror_msg,thesender,))
                                    continue;
                                cursor2.execute('SELECT count(*) FROM users WHERE phone = ?',(fullnum,))
                                for ucount in cursor2:
                                    ucount = ucount[0]
                                
                                if(ucount==0):
                                    cursor2.execute('INSERT INTO users("nick","phone","service") VALUES(?,?,"start")', (numstr,fullnum,))
                                    cursor.execute('INSERT INTO followers("follower","following") VALUES(?,?)',(numstr,thesendernick,))
                                    thefolwr_notify = "From ShoutJam: @"+thesendernick+" ("+thesender+") has added you as a follower. You will now receive all shouts of this user. Send @help to "+shoutJamNumber+" for help and visit shoutjamit.com for more info"
                                    cursor.execute('INSERT INTO psq("msg","phone") VALUES(?,?)', (thefolwr_notify,fullnum,))
                                    the_confirm_notify = "You have successfully added "+the_nickname+" to your followers list"
                                    cursor.execute('INSERT INTO psq("msg","phone") VALUES(?,?)', (the_confirm_notify,thesender,))
                                else:
                                    cursor2.execute('SELECT nick FROM users WHERE phone = ?',(fullnum,))
                                    nickdata = cursor2.fetchone()
                                    thenick = nickdata[0]
                                    if(re.match("num:",thenick)!=None):
                                        cursor.execute('SELECT count(*) FROM followers WHERE follower = ? AND following = ?',(numstr,thesendernick,))
                                        for youmefol in cursor:
                                            youmefol = youmefol[0]
                                        if(youmefol==0):
                                            cursor.execute('INSERT INTO followers("follower","following") VALUES(?,?)',(numstr,thesendernick,))
                                            thefolwr_notify = "From ShoutJam: @"+thesendernick+" ("+thesender+") has added you as a follower. You will now receive all shouts of this user. Send @help to "+shoutJamNumber+" for help and visit shoutjamit.com for more info"
                                            cursor.execute('INSERT INTO psq("msg","phone") VALUES(?,?)', (thefolwr_notify,fullnum,))
                                            the_confirm_notify = "You have successfully added "+the_nickname+" to your followers list"
                                            cursor.execute('INSERT INTO psq("msg","phone") VALUES(?,?)', (the_confirm_notify,thesender,))
                            except:
                                print "Didn't find sender nick"
                        except:
                            print " "

                elif(re.compile("@follow ", re.IGNORECASE).match(msg_cnt)!=None):
                    the_nickname = string.split(msg_cnt," ")
                    the_nickname = string.lower(the_nickname[1])
                    cursor.execute('SELECT nick FROM users WHERE phone = ?',(thesender,))
                    try:
                        thesendernick = cursor.fetchone()[0]
                        cursor2.execute('SELECT count(*) from followers WHERE follower = ?',(thesendernick,))
                        for folcount in cursor2:
                            folcount = folcount[0]
                        if(folcount!=5):
                            cursor2.execute('SELECT nick,phone,service FROM users WHERE nick = ?',(the_nickname,))
                            cursor.execute('SELECT count(*) from followers WHERE follower = ? AND following =?',(thesendernick,the_nickname,))
                            for youmefol in cursor:
                                youmefol = youmefol[0]
                            if(youmefol==0):
                                try:
                                    nickdata = cursor2.fetchone()
                                    thenick = nickdata[0]
                                    thephone = nickdata[1]
                                    theservice = nickdata[2]
                                    cursor.execute('INSERT INTO followers("follower","following") VALUES(?,?)',(thesendernick,thenick,))
                                    if(theservice=="start"):
                                        if(re.match("num:",thesendernick)!=None):
                                            thefollow_notify = "User with the phone "+thephone+" is now following your updates"
                                        else:
                                            thefollow_notify = "@"+thesendernick+" is now following your updates"
                                        cursor.execute('INSERT INTO psq("msg","phone") VALUES(?,?)', (thefollow_notify,thephone,))
                                except:
                                    print "Didn't find nick to follow"
                        else:
                            thefollow_notify = "You can follow only upto 5 people's updates but any number of people can follow yours. This limit is temporary and will be lifted soon"
                            cursor.execute('INSERT INTO psq("msg","phone") VALUES(?,?)', (thefollow_notify,thephone,))
                            
                    except:
                        print "Didn't find sender nick"
                        fullnum = thesender
                        numstr = "num:"+thesender[3:0]
                        
                        cursor2.execute('SELECT nick,phone,service FROM users WHERE nick = ?',(the_nickname,))
                        try:
                            nickdata = cursor2.fetchone()
                            thenick = nickdata[0]
                            thephone = nickdata[1]
                            theservice = nickdata[2]
                            cursor.execute('SELECT count(*) from users WHERE phone = ?',(fullnum,))
                            for ucount in cursor:
                                ucount = ucount[0]
                            if(ucount==0):
                                cursor2.execute('INSERT INTO users("nick","phone","service") VALUES(?,?,"start")', (numstr,fullnum,))
                            cursor.execute('INSERT INTO followers("follower","following") VALUES(?,?)',(fullnum,thenick,))
                            the_confirm_notify = "From ShoutJam: You will now receive all shouts of "+thenick+". Send @help to xxxxxxxxxx for help and visit shoutjamit.com for more info"
                            cursor.execute('INSERT INTO psq("msg","phone") VALUES(?,?)', (the_confirm_notify,fullnum,))
                            if(theservice=="start"):
                                thefolwr_notify = "The user with the number "+thesender+" is now following your updates";
                                cursor.execute('INSERT INTO psq("msg","phone") VALUES(?,?)', (thefolwr_notify,thephone,))
                        except:
                            print "Didn't find nick to follow"
                        
                        
                elif(re.compile("@leave ", re.IGNORECASE).match(msg_cnt)!=None):
                    the_nickname = string.split(msg_cnt," ")
                    the_nickname = string.lower(the_nickname[1])
                    cursor.execute('SELECT nick FROM users WHERE phone = ?',(thesender,))
                    try:
                        thesendernick = cursor.fetchone()[0]
                        cursor2.execute('SELECT nick,phone,service FROM users WHERE phone = ?',(thesender,))
                        try:
                            nickdata = cursor2.fetchone()
                            thenick = nickdata[0]
                            thephone = nickdata[1]
                            theservice = nickdata[2]
                            print thenick+" leaving "+the_nickname
                            thesqlstatement = "DELETE FROM followers WHERE follower = '"+thenick+"' AND following = '"+the_nickname+"'"
                            print thesqlstatement
                            cursor.execute(thesqlstatement)
                        except:
                            print " Didn't find nick to unfollow"
                    except:
                        print " Didn't find sender nick"
    
                elif(re.compile("@join ", re.IGNORECASE).match(msg_cnt)!=None):
                    the_nickname = string.split(msg_cnt," ")
                    the_nickname = string.lower(the_nickname[1])
                
                    if(len(the_nickname)<4 or len(the_nickname)>30 or (re.match('[0-9a-zA-Z\-_]*$',the_nickname)==None) or re.compile("shoutjam", re.IGNORECASE).match(the_nickname)!=None or re.compile("sjstat", re.IGNORECASE).match(the_nickname)!=None or re.compile("start", re.IGNORECASE).match(the_nickname)!=None or re.compile("stop", re.IGNORECASE).match(the_nickname)!=None or re.compile("help", re.IGNORECASE).match(the_nickname)!=None or re.compile("follow", re.IGNORECASE).match(the_nickname)!=None or re.compile("leave", re.IGNORECASE).match(the_nickname)!=None):
                        themsgtosend = "Your nickname should consist of atleast 4 characters and can only contain letters and numbers"
                        cursor.execute('INSERT INTO psq("msg","phone") VALUES(?,?)', (themsgtosend,thesender,))
                    else:
                        cursor.execute('SELECT id,nick FROM users WHERE phone = ?',(thesender,))
                        try:
                            nickdata  = cursor.fetchone()
                            id = nickdata[0]
                            the_old_nickname = nickdata[1]
                            if(re.match("num:",the_old_nickname)==None):
                                themsg = "You are already registered with the nickname "+the_old_nickname
                                cursor.execute('INSERT INTO psq("msg","phone") VALUES(?,?)', (themsg,thesender,))
                            else:
                                cursor.execute('SELECT count(*) FROM users WHERE nick = ?',(the_nickname,))
                                for ucount in cursor:
                                    ucount=ucount[0]
                                if(ucount!=0):
                                    themsg = "The nickname "+the_nickname+" is already in use. Please choose a different one"
                                    cursor.execute('INSERT INTO psq("msg","phone") VALUES(?,?)', (themsg,thesender,))
                                else:
                                    print the_nickname, thesender
                                    thenewsender = string.split(thesender,"+91")[1]
                                    numstr = "num:"+thenewsender
                                    cursor.execute('SELECT count(*) FROM users WHERE nick = ?',(numstr,))
                                    for ucount in cursor:
                                        ucount=ucount[0]
                                    if(ucount==1):
                                        cursor.execute("UPDATE followers SET follower = ? WHERE follower= ?",(the_nickname,numstr,))
                                        cursor.execute("UPDATE followers SET following = ? WHERE following= ?",(the_nickname,numstr,))
                                        cursor.execute("UPDATE followers SET following = ? WHERE following= ?",(the_nickname,numstr,))
                                        cursor.execute("UPDATE users SET nick = ? WHERE nick= ?",(the_nickname,numstr,))
                                    else:
                                        cursor2.execute('INSERT INTO users("nick","phone","service") VALUES(?,?,"start")', (the_nickname,thesender,))
                                    print "Joined users..."
                                    cursor2.execute("SELECT * from users");
                                    for eachuser in cursor2:
                                        print eachuser
                                    themsg = "Hi "+the_nickname+"! Welcome to ShoutJam!\nSend \n@all <msg>\n to send a shout-out to all your friends. Your friends are those who follow your shouts.\nSend @follow <user>\nto follow a person. On following a person you'll receive all shout-outs of that person.\nSend @help for more ShoutJam commands"
                                    cursor.execute('INSERT INTO psq("msg","phone") VALUES(?,?)', (themsg,thesender,))
                                    print thesender+" joined"
                        except:
                            cursor.execute('SELECT count(*) FROM users WHERE nick = ?',(the_nickname,))
                            for ucount in cursor:
                                ucount=ucount[0]
                            if(ucount!=0):
                                themsg = "The nickname "+the_nickname+" is already in use. Please choose a different one"
                                cursor.execute('INSERT INTO psq("msg","phone") VALUES(?,?)', (themsg,thesender,))
                            else:
                                print the_nickname, thesender
                                thenewsender = thesender
                                numstr = "num:"+thenewsender[3:0]
                                cursor.execute('SELECT count(*) FROM users WHERE nick = ?',(numstr,))
                                for ucount in cursor:
                                    ucount=ucount[0]
                                if(ucount==1):
                                    cursor.execute("UPDATE followers SET follower = ? WHERE follower= ?",(the_nickname,numstr,))
                                    cursor.execute("UPDATE followers SET following = ? WHERE following= ?",(the_nickname,numstr,))
                                    cursor.execute("UPDATE followers SET following = ? WHERE following= ?",(the_nickname,numstr,))
                                    cursor.execute("UPDATE users SET nick = ? WHERE nick= ?",(the_nickname,numstr,))
                                else:
                                    cursor2.execute('INSERT INTO users("nick","phone","service") VALUES(?,?,"start")', (the_nickname,thesender,))
                                print "Joined users..."
                                cursor2.execute("SELECT * from users");
                                for eachuser in cursor2:
                                    print eachuser
                                themsg = "Hi "+the_nickname+"! Welcome to ShoutJam!\nSend \n@all <msg>\n to send a shout-out to all your friends. Your friends are those who follow your shouts.\nSend @follow <user>\nto follow a person. On following a person you'll receive all shout-outs of that person.\nSend @help for more ShoutJam commands"
                                cursor.execute('INSERT INTO psq("msg","phone") VALUES(?,?)', (themsg,thesender,))
                                print thesender+" joined"
                elif(re.compile("@stop", re.IGNORECASE).match(msg_cnt)!=None):
                    cursor.execute("UPDATE users SET service = 'stop' WHERE phone= ?",(thesender,))
                elif(re.compile("@start", re.IGNORECASE).match(msg_cnt)!=None):
                    cursor.execute("UPDATE users SET service = 'start' WHERE phone= ?",(thesender,))
                elif(re.compile("@help", re.IGNORECASE).match(msg_cnt)!=None):
                    print thesender+" asked for help"

                    cursor.execute('SELECT nick FROM users WHERE phone = ?',(thesender,))
                    try:
                        thesendernick = cursor.fetchone()[0]
                        
                        helpmsg = "ShoutJam Commands Help:\n @all <msg>\n to send a shout-out to all your friends.\n@follow <user> to follow a person's shout.\n@leave <user> to stop following a person.\n@<user> <msg> to send shout-out to a particular nick.\nSend @stop or @start to pause or resume msgs\n@join <user> to join ShoutJam. Visit shoutjamit.com for more info"
                    except:
                        helpmsg = "ShoutJam: send @join <username> to join ShoutJam to enable more features. Send @stop to stop receiving msgs and @start to resume."
                    cursor.execute('INSERT INTO psq("msg","phone") VALUES(?,?)', (helpmsg,thesender,))            
                elif(re.compile("@sjstat", re.IGNORECASE).match(msg_cnt)!=None):
                    cursor.execute("SELECT count(*) FROM users")
                    for ucount in cursor:
                        ucount=ucount[0]
                    thesysmsg = "sjstat "+str(ucount)
                    cursor.execute('INSERT INTO psq("msg","phone") VALUES(?,?)', (thesysmsg,thesender,))
                elif(re.compile("@\w", re.IGNORECASE).match(msg_cnt)!=None):
                    the_act_msg = string.split(msg_cnt," ")
                    tonick = the_act_msg[0]
                    tonick = string.split(tonick, "@")
                    tonick = string.lower(tonick[1])
                    del the_act_msg[0]
                    the_act_msg = string.join(the_act_msg)
    
                    cursor.execute('SELECT nick FROM users WHERE phone = ?',(thesender,))
                    try:
                        thesendernick = cursor.fetchone()[0]
                        if(thesendernick[0:4]=="num:"):
                            theerror_msg = "YOu must join ShoutJam using the\n@join <username>\ncommand before sending messages to others"
                            cursor.execute('INSERT INTO psq("msg","phone") VALUES(?,?)', (theerror_msg,thesender,))
                            continue;
                        cursor2.execute('SELECT nick,phone,service FROM users WHERE nick = ?',(tonick,))
                        try:
                            nickdata = cursor2.fetchone()
                            thenick = nickdata[0]
                            thephone = nickdata[1]
                            theservice = nickdata[2]
                            themsgtosend = "@"+thesendernick+": "+the_act_msg
                            if(theservice=="start"):
                                cursor.execute('INSERT INTO psq("msg","phone") VALUES(?,?)', (themsgtosend,thephone,))
                        except:
                            print the_act_msg
                            print " Didn't find nick to send"
                    except:
                        print " Didn't find sender nick"
                else:
                    # to consider any SMS without ShoutJam commands as my personal SMS and save it for me to check later
                    cursor.execute('INSERT INTO personalmsgs("msg","phone") VALUES(?,?)', (msg_cnt,thesender,))


