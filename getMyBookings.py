from __future__ import print_function
import httplib2
import os
import os.path
import pprint
import sys
import base64
import slate
import parse
import codecs

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

# script will fetch all bookins since this day. Set to empty string to get ALL bookings
startdate = ' after:2016/04/06'
# startdate = ''


try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gmail-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Gmail API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'gmail-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def main():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    # fetch all messages from DB:
    messages = service.users().messages().list(userId='me', q='from:buchungsbestaetigung@bahn.de'+startdate).execute()

    # write head for the output CSV

    file = codecs.open("bookings.csv", "w", "utf-8")
    file.write(u'Date,From,To,Ticket,Price\n')
    file.close()

    # go through all messages, download and parse the attached PDF for each
    file = codecs.open("bookings.csv", "a", "utf-8")
    for m in messages['messages']:
        msg = service.users().messages().get(userId='me', id=m['id']).execute()

        body = msg['payload']['parts'][0]['body']
        if('attachmentId') in body:
            attachmentID = body['attachmentId']
            filename = msg['payload']['parts'][0]['filename']

            # only download the PDF if we don't have it yet:
            if os.path.exists(filename):
                print (filename + " alread downloaded")
            else:
                response = service.users().messages().attachments().get(userId='me', id=attachmentID, messageId=m['id']).execute()
                file_data = base64.urlsafe_b64decode(response['data'].encode('UTF-8'))

                with open(filename, 'w') as f:
                    f.write(file_data)


            try:
                date, start, dest, price = parse.parseBooking(filename)
                file.write(date + ",'" + start + "','" + dest + "','" + filename + "'," + price + "\n")
            except Exception as e:
                print("Error processing " +filename)
                print(e)
                file.write(",,,'" + filename + "',\n")



        else:
            print("Msg " + str(m['id']) + " doesn't seem to have an attachment.")


    file.close()



if __name__ == '__main__':
    main()
