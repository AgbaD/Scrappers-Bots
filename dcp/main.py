#!/usr/bin/python
# Author:	@AgbaD | @agba_dr3

import os
import imaplib
import email
import webbrowser
from email.header import decode_header


username = "blankgodd33@gmail.com"
password = "mefghjrbuaftxnvc"

def clean(text):
	return "".join(c if c.isalnum() else "_" for c in text)


def login(username, password):
	# imap class with ssl
	imap = imaplib.IMAP4_SSL("imap.gmail.com")
	# auth
	imap.login(username, password)
	return imap


def get_messages(imap, subject_query=None):
	status, messages = imap.select("INBOX")
	# total number of email
	messages = int(messages[0])

	for i in range(messages, messages-3, -1):
		res, msg = imap.fetch(str(i), '(RFC822)')
		for response in msg:
			if isinstance(response, tuple):
				msg = email.message_from_bytes(response[1])
				subject, encoding = decode_header(msg["Subject"])[0]
				if isinstance(subject, bytes):
					subject = subject.decode(encoding)


if __name__ == "__main__":
	imap = login(username, password)
	get_messages(imap)
