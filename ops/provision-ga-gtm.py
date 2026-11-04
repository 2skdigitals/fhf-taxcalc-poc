#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Provision GA4 + GTM for the FHF tax-calculator blocks under 2skdigitals@.

Run AFTER ops/google-auth.py has saved ~/.hermes/credentials/fhf-ga-gtm-token.json.

Creates, idempotently (safe to re-run):
  GA4  : account "2SK Solutions" (if none) · property "FHF Tax Calculator POC"
         · web stream · 5 custom dimensions
  GTM  : account (if none) · container "fhf-taxcalc-poc" · 5 data-layer variables
         · 1 custom-event trigger · 3 tags · published version

Prints every id at the end. Nothing is deleted, ever.
"""
import json, os, sys, urllib.error, urllib.parse, urllib.request

TOK = os.path.expanduser("~/.hermes/credentials/fhf-ga-gtm-token.json")
STREAM_URI = "https://2skdigitals.github.io/fhf-taxcalc-poc/"
GA_ACCOUNT_NAME = "2SK Solutions"
PROPERTY_NAME = "FHF Tax Calculator POC"
CONTAINER_NAME = "fhf-taxcalc-poc"
EVENTS = ["calc_started", "calc_result_shown", "qr_view", "rail_click",
          "email_capture", "receipt_request", "receipt_fulfilled", "donation_self_report"]
DIMS = [("rail", "Rail"), ("state", "Device state"), ("donation_type", "Donation type"),
        ("band", "Income band (coarse)"), ("cap_state", "Cap state")]

BRIDGE_HTML = """<script>
window.dataLayer = window.dataLayer || [];
window.addEventListener("message", function (e) {
  var d = e.data;
  if (!d || d.source !== "fhf-taxcalc") return;
  if (d.type === "deeplink") {
    dataLayer.push({event:"fhf_deeplink_test", rail:d.rail, phase:d.phase, blocked:!!d.blocked});
    return;
  }
  if (d.type !== "event") return;
  dataLayer.push(Object.assign({event:d.name}, d.params || {}));
});
</script>"""


def token():
    d = json.load(open(TOK))
    body = urllib.parse.urlencode({
        "client_id": d["client_id"], "client_secret": d["client_secret"],
        "refresh_token": d["refresh_token"], "grant_type": "refresh_token"}).encode()
    req = urllib.request.Request(d["token_uri"], data=body)
    return json.load(urllib.request.urlopen(req))["access_token"]


T = token()


def api(method, url, payload=None, base="https://analyticsadmin.googleapis.com/v1beta"):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url if url.startswith("http") else base + url, data=data, method=method,
                                 headers={"Authorization": "Bearer " + T, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as r:
            body = r.read().decode()
            return json.loads(body) if body.strip() else {}
    except urllib.error.HTTPError as e:
        detail = e.read().decode()
        print(f"  ! {method} {url} -> {e.code}\n    {detail[:600]}")
        raise


def ga(url, payload=None, method="POST"):
    return api(method, url, payload)


def gtm(method, url, payload=None):
    return api(method, url, payload, base="https://www.googleapis.com/tagmanager/v2")


print("== GA4 ==")
accounts = ga("/accounts", method="GET").get("accounts", [])
print("  accounts:", [a["name"] for a in accounts])
acct = next((a for a in accounts if a.get("displayName") == GA_ACCOUNT_NAME), None)
if not acct:
    acct = ga("/accounts", {"displayName": GA_ACCOUNT_NAME, "regionCode": "HK"})
    print("  + created account", acct["name"])
else:
    print("  · reuse account", acct["name"])
acct_id = acct["name"].split("/")[1]

props = ga(f"/properties?filter=parent:accounts/{acct_id}", method="GET").get("properties", [])
prop = next((p for p in props if p.get("displayName") == PROPERTY_NAME), None)
if not prop:
    prop = ga(f"/properties?parent=accounts/{acct_id}".split("?")[0],
              {"parent": f"accounts/{acct_id}", "displayName": PROPERTY_NAME,
               "timeZone": "Asia/Hong_Kong", "currencyCode": "HKD", "industryCategory": "OTHER"})
    print("  + created property", prop["name"])
else:
    print("  · reuse property", prop["name"])
prop_id = prop["name"].split("/")[1]

streams = ga(f"/properties/{prop_id}/dataStreams", method="GET").get("dataStreams", [])
stream = streams[0] if streams else ga(f"/properties/{prop_id}/dataStreams", {
    "type": "WEB_DATA_STREAM", "displayName": "POC blocks", "webStreamData": {"defaultUri": STREAM_URI}})
MID = (stream.get("webStreamData") or {}).get("measurementId")
print("  measurement id:", MID)

have = {d["parameterName"] for d in ga(f"/properties/{prop_id}/customDimensions", method="GET").get("customDimensions", [])}
for pname, label in DIMS:
    if pname in have:
        continue
    ga(f"/properties/{prop_id}/customDimensions",
       {"parameterName": pname, "displayName": label, "scope": "EVENT"})
    print("  + dimension", pname)

print("\n== GTM ==")
gaccounts = gtm("GET", "/accounts").get("account", [])
print("  accounts:", [a["name"] for a in gaccounts])
gacct = next((a for a in gaccounts if a.get("name") == GA_ACCOUNT_NAME), None)
if not gacct:
    gacct = gtm("POST", "/accounts", {"name": GA_ACCOUNT_NAME, "shareData": True})
    print("  + created account", gacct["accountId"])
gid = gacct["accountId"]

conts = gtm("GET", f"/accounts/{gid}/containers").get("container", [])
cont = next((c for c in conts if c.get("name") == CONTAINER_NAME), None)
if not cont:
    cont = gtm("POST", f"/accounts/{gid}/containers", {"name": CONTAINER_NAME, "usageContext": ["web"]})
    print("  + created container", cont["containerId"])
cid = cont["containerId"]
ws = gtm("GET", f"/accounts/{gid}/containers/{cid}/workspaces").get("workspace", [])[0]["workspaceId"]
print("  container id:", cid, "workspace:", ws)

W = f"/accounts/{gid}/containers/{cid}/workspaces/{ws}"
existing_vars = {v["name"] for v in gtm("GET", W + "/variables").get("variable", [])}
DLVS = DIMS + [("host_page", "Host page")]
for pname, label in DLVS:
    nm = f"DLV - {pname}"
    if nm in existing_vars:
        continue
    gtm("POST", W + "/variables", {"name": nm, "type": "v", "parameter": [
        {"type": "integer", "key": "dataLayerVersion", "value": "2"},
        {"type": "boolean", "key": "setDefaultValue", "value": "false"},
        {"type": "template", "key": "dataLayerName", "value": pname}]})
    print("  + variable", nm)

existing_tr = {t["name"] for t in gtm("GET", W + "/triggers").get("trigger", [])}
TR_NAME = "CE — FHF widget events"
tr_id = None
for t in gtm("GET", W + "/triggers").get("trigger", []):
    if t["name"] == TR_NAME:
        tr_id = t["triggerId"]
if not tr_id:
    tr = gtm("POST", W + "/triggers", {
        "name": TR_NAME, "type": "customEvent",
        "customEventFilter": [{"type": "matchRegex", "parameter": [
            {"type": "template", "key": "arg0", "value": "{{_event}}"},
            {"type": "template", "key": "arg1", "value": "^(" + "|".join(EVENTS) + ")$"}]}]})
    tr_id = tr["triggerId"]
    print("  + trigger", tr_id)

existing_tags = {t["name"] for t in gtm("GET", W + "/tags").get("tag", [])}

if "FHF — widget bridge" not in existing_tags:
    gtm("POST", W + "/tags", {"name": "FHF — widget bridge", "type": "html", "firingTriggerId": ["2147479553"],
                              "parameter": [{"type": "template", "key": "html", "value": BRIDGE_HTML},
                                            {"type": "boolean", "key": "supportDocumentWrite", "value": "false"}]})
    print("  + tag bridge")

if "GA4 — config" not in existing_tags:
    # GTM runs INSIDE the iframe, so GA4 would report the embed URL as the page.
    # Override page_location with the embedding page captured from document.referrer.
    try:
        gtm("POST", W + "/tags", {"name": "GA4 — config", "type": "gaawc", "firingTriggerId": ["2147479553"],
                                  "parameter": [
                                      {"type": "template", "key": "measurementId", "value": MID},
                                      {"type": "list", "key": "fieldsToSet", "list": [
                                          {"type": "map", "map": [
                                              {"type": "template", "key": "name", "value": "page_location"},
                                              {"type": "template", "key": "value", "value": "{{DLV - host_page}}"}]}]}]})
        print("  + tag GA4 config (page_location overridden)")
    except Exception:
        # fieldsToSet shape rejected → still create a working config tag
        gtm("POST", W + "/tags", {"name": "GA4 — config", "type": "gaawc", "firingTriggerId": ["2147479553"],
                                  "parameter": [{"type": "template", "key": "measurementId", "value": MID}]})
        print("  + tag GA4 config (no page override — field shape rejected)")

if "GA4 — FHF widget event" not in existing_tags:
    gtm("POST", W + "/tags", {"name": "GA4 — FHF widget event", "type": "gaawe", "firingTriggerId": [tr_id],
                              "parameter": [
                                  {"type": "template", "key": "eventName", "value": "{{Event}}"},
                                  {"type": "template", "key": "measurementId", "value": MID},
                                  {"type": "list", "key": "eventParameters", "list": [
                                      {"type": "map", "map": [
                                          {"type": "template", "key": "name", "value": pname},
                                          {"type": "template", "key": "value", "value": "{{DLV - " + pname + "}}"}]}
                                      for pname, _ in DIMS]}]})
    print("  + tag GA4 event")

ver = gtm("POST", W + ":create_version", {"name": "POC v1", "notes": "bridge + GA4 config + widget events"})
publish = gtm("POST", f"/accounts/{gid}/containers/{cid}/versions/{ver['containerVersion']['containerVersionId']}:publish")
print("  · published version", ver["containerVersion"]["containerVersionId"])

print("\n== RESULT ==")
print(json.dumps({"gaAccount": acct_id, "gaProperty": prop_id, "gaMeasurementId": MID,
                  "gtmAccount": gid, "gtmContainer": cid,
                  "containerSnippet": f"GTM-{cont.get('publicId', cid)}"}, indent=2))
