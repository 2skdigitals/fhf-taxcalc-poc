#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""One-time OAuth grant for creating the FHF GA4 property + GTM container
under whichever Google account authorises this flow (must be 2skdigitals@).

Writes ~/.hermes/credentials/fhf-ga-gtm-token.json on success.
Nothing is created here — this only obtains the write scopes.
"""
import json, os, sys
from google_auth_oauthlib.flow import InstalledAppFlow

CLIENT = os.path.expanduser("~/2SK/fred-hollows/credentials/client_secret.json")
OUT = os.path.expanduser("~/.hermes/credentials/fhf-ga-gtm-token.json")
PORT = 8770
if not os.path.exists(CLIENT):
    CLIENT = os.path.expanduser("~/.hermes/credentials/client_secret.json")

SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/analytics.edit",
    "https://www.googleapis.com/auth/analytics.manage.users",
    "https://www.googleapis.com/auth/tagmanager.edit.containers",
    "https://www.googleapis.com/auth/tagmanager.edit.containerversions",
    "https://www.googleapis.com/auth/tagmanager.publish",
    "https://www.googleapis.com/auth/tagmanager.manage.users",
]

flow = InstalledAppFlow.from_client_secrets_file(CLIENT, scopes=SCOPES)
# open_browser=False: the URL is printed so it can be opened on this machine manually
creds = flow.run_local_server(port=PORT, open_browser=False, prompt="consent",
                              authorization_prompt_message="\nOPEN THIS URL:\n{url}\n")

creds_dict = {
    "token": creds.token,
    "refresh_token": creds.refresh_token,
    "token_uri": creds.token_uri,
    "client_id": creds.client_id,
    "client_secret": creds.client_secret,
    "scopes": creds.scopes,
    "expiry": creds.expiry.isoformat() if creds.expiry else None,
}
with open(OUT, "w") as f:
    json.dump(creds_dict, f, indent=2)
os.chmod(OUT, 0o600)

# who authorised?
try:
    import urllib.request
    req = urllib.request.Request("https://www.googleapis.com/oauth2/v3/userinfo",
                                 headers={"Authorization": "Bearer " + creds.token})
    who = json.load(urllib.request.urlopen(req))
    print("AUTHORIZED_AS", who.get("email"))
except Exception as e:
    print("AUTHORIZED_AS unknown:", e)
print("SAVED", OUT)
