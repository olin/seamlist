import mailbox
import email
from email.Parser import Parser

box = mailbox.mbox('helpme.mbox')

p = Parser()

#x = p.parsestr(box[1].get_payload(decode=True))
#print x.get_payload(decode=True)

#print box[1].get_payload(decode=True)

def msg_body(msg):
	body = None
	for part in msg.walk():
		if part.get_content_type() in ['multipart/mixed', 'text/plain']:
			body = part
	return body

print msg_body(box[2]).get_payload(decode=True)

#msg = email.message_from_string(msg.get_payload(decode=True))
#print msg
#print msg.get('content-type')

