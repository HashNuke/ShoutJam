import inbox, messaging, json, string
from socket import *
from sysinfo import battery

'''
change this if you want to change the control message. Sending this will send you back the number of users and the phone's battery usage. Keep it secret.
'''
controlMessage = "sjstat"

pushed=1
sockstatus="first"

print  u"Initializing..."
while(1):
    conntest=0
    while(conntest!=1):
        try:
            if(sockstatus!="first"):
                client.close()
                sock.close()
            sock = socket(AF_BT, SOCK_STREAM)
            port = bt_rfcomm_get_available_server_channel(sock)
            sock.bind(("", port))
 
            set_security(sock, AUTHOR)
            sock.listen(3)
 
            bt_advertise_service(u"ShoutJamServer", sock, True, RFCOMM)
            print "waiting for conn"
            client, addr = sock.accept()
            sockstatus=""
            conntest=1
            print "connected"
        except:
            conntest=0
            print "Restart failed"
    
    while(1):
        if(pushed!=0):
            inboxtest=0
            while(inboxtest!=1):
                inboxtest=0
                try:
                    ibox = inbox.Inbox()
                    allmsgs = ibox.sms_messages()
                    inboxtest=1
                except:
                    inboxtest=0
            pushdata = []
            readcount=0
            for msg_id in allmsgs:
                if(readcount!=10):
                    if(ibox.unread(msg_id)==1):
                        try:                    
                            thecontent = ibox.content(msg_id)
                            thecontent = thecontent[0:300]
                        except:
                            continue
                        thesender = ibox.address(msg_id)
                        msgdata = {'msg': thecontent, 'sender': thesender}
                        pushdata.append(msgdata)
                        ibox.delete(msg_id)
                        readcount=readcount+1
                else:
                    readcount=0
                    break
        outputJSON = json.write({'payload': pushdata })
        try:
            client.send(outputJSON)
            pushed=1
        except:
            print "broke during send"
            pushed=0
        
        try:
            rdata = client.recv(4096)
            recvd = 1
        except:
            recvd = 0
    
        try:
            inputJSON = json.read(rdata)
        except:
            print "broke during recv"
            continue
        if(inputJSON['payload']!=[]):
            for e_msg in inputJSON['payload']:
                checkme = e_msg['msg']
                the_act_msg = string.split(checkme," ")
                the_users = the_act_msg[1]
                the_sjstat = the_act_msg[0]
                
                # check for control message and send details
                if(the_sjstat==controlMessage):
                    themsg = "battery level: "+str(battery())+" Users: "+str(the_users)
                else:
                    themsg = e_msg['msg']
                sendto = e_msg['to']
                sendtest=0
                while(sendtest!=1):
                    try:
                        messaging.sms_send(sendto,themsg)
                        sendtest=1
                    except:
                        sendtest=0

