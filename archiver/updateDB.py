import mailbox
import email
import quopri

#http://stackoverflow.com/questions/7166922/extracting-the-body-of-an-email-from-mbox-file-decoding-it-to-plain-text-regard

import mailbox
import quopri,base64

def myconvert(encoded,ContentTransferEncoding):
    if ContentTransferEncoding == 'quoted-printable':
        result = quopri.decodestring(encoded)
    elif ContentTransferEncoding == 'base64':
        result = base64.b64decode(encoded)
    return result

mboxfile = 'Emails2.mbox' 

#for msg in mailbox.mbox(mboxfile):
msg = mailbox.mbox(mboxfile)[0]

print msg.get_content_type()

#print msg.get_payload()
if msg.is_multipart():    #Walk through the parts of the email to find the text body.
    print "Multipart"
    for part in msg.walk():
        if part.is_multipart(): # If part is multipart, walk through the subparts.
            for subpart in part.walk():
                if subpart.get_content_type() == 'text/plain':
                    body = subpart.get_payload() # Get the subpart payload (i.e the message body)
                    print "body1"
                for k,v in subpart.items():
                        if k == 'Content-Transfer-Encoding':
                            cte = v             # Keep the Content Transfer Encoding
        elif subpart.get_content_type() == 'text/plain':
            body = part.get_payload()           # part isn't multipart Get the payload
            print "Body2"
            for k,v in part.items():
                if k == 'Content-Transfer-Encoding':
                    cte = v                      # Keep the Content Transfer Encoding

#print(body)
#print('Body is of type:',type(body))
body = myconvert(body,cte)
#print(body)

"""

def walkMsg(msg):
    for part in msg.walk():
        print part.get_content_type()
        if part.get_content_type() == "multipart/alternative":
            continue
        yield part.get_payload(decode=True)


mbox = mailbox.mbox('parsed.mbox')

print mbox[0].get_payload(decode=True)

#print [x for x in walkMsg(mbox[0])]

"""

"""
for message in mbox:
    print quopri.decodestring(message.get_payload())

# ['From', 'Date', 'Subject', 'Message-ID']

#for message in mbox:
#    print message['subject']
    
"""


