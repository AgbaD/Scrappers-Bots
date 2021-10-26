
#!/usr/bin/python
# Author:	@AgbaD | @agba_dr3

import re
import os
import imaplib
import email
from getpass import getpass
from email.header import decode_header


def clean(text):
	return "".join(c if c.isalnum() else "_" for c in text)


def login(username, password):
	# imap class with ssl
	imap = imaplib.IMAP4_SSL("imap.gmail.com")
	# auth
	imap.login(username, password)
	return imap


def get_messages(imap, pattern=None):
	status, messages = imap.select("INBOX")
	# total number of email
	messages = int(messages[0])

	for i in range(messages, messages-700, -1):
		res, msg = imap.fetch(str(i), '(RFC822)')
		for response in msg:
			if isinstance(response, tuple):
				msg = email.message_from_bytes(response[1])
				subject, encoding = decode_header(msg["Subject"])[0]
				if isinstance(subject, bytes):
					try:
						subject = subject.decode(encoding)
					except:
						subject = subject.decode()
				sender, encoding = decode_header(msg.get("From"))[0]
				if isinstance(sender, bytes):
					try:
						sender = sender.decode(encoding)
					except:
						sender = sender.decode()
				a = 1
				if re.search(pattern, subject):
					print(subject, "-----  downloaded")
					folder = clean(subject)
					if not os.path.isdir(folder):
						os.mkdir(folder)
					if msg.is_multipart():
						for part in msg.walk():
							content_type = part.get_content_type()
							content_disp = str(part.get("Content-Disposition"))
							try:
								body = part.get_payload(decode=True).decode()
							except:
								pass
							if content_type == "text/plain" and "attachment" not in content_disp:
								filename = f"{a}.txt"
								path = os.path.join(folder, filename)
								open(path, 'w').write(body)
								a += 1
							else:
								pass 
					else:
						content_type = msg.get_content_type()
						body = msg.get_payload(decode=True).decode()
					filename = None
					if content_type == "text/plain":
						filename = f"{a}.txt"
					elif content_type == "text/html":
						filename = f"{a}.html"
					path = os.path.join(folder, filename)
					open(path, 'w').write(body)


def close_connection(imap):
	imap.close()
	imap.logout()


if __name__ == "__main__":
	username = input("Enter your email address: ") or "blankgodd33@gmail.com"
	password = getpass("Enter your password: ") or "zirkxpfvaltvaswo"
	imap = login(username, password)
	print()
	print("Logging user in....")
	print()
	pattern = input("Enter subject pattern: ")
	print()
	print("Searching...")
	print()
	print("Downloading...")
	print()
	get_messages(imap, pattern)
	print("Search and download complete")
	print()
	print("Closing connection...")
	close_connection(imap)

