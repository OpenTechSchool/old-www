import sys
try:
    import argparse
except ImportError:
    print "Please run with python >2.7"
    sys.exit(1)

try:
    import gdata.apps.groups.client
except ImportError:
    print "Please install py-gdata"
    sys.exit(1)


parser = argparse.ArgumentParser(description='')
parser.add_argument('email')
parser.add_argument('--filename', default="groups.md")
parser.add_argument('--domain', default="opentechschool.org")
parser.add_argument('--password')

args = parser.parse_args()

BASE_LINK = "https://groups.google.com/a/%s/forum/?fromgroups#!forum/" % args.domain

HEADER = """---
layout: main
title: Mailinglists
---


# MailingList

"""

FORMAT_ENTRY = """
### [{name}]({link})

{desc}
"""

password = args.password
if not password:
    password = raw_input("Password please: ")


groupClient = gdata.apps.groups.client.GroupsProvisioningClient(domain=args.domain)
groupClient.ClientLogin(email=args.email, password=password, source='apps')
groups = groupClient.RetrieveAllGroups()


collection = {
    "coaches": [],
    "team": [],
    "main": []
}


for group in groups.entry:
    name = group.group_name
    email = group.group_id
    if "-deleted-" in email:
        continue
    mail_handle = email.split("@", 1)[0]
    desc = group.description
    group_cat = mail_handle.split(".", 1)[0]
    try:
        listing = collection[group_cat]
    except KeyError:
        listing = collection["main"]

    listing.append({
            "name": name,
            "email": email,
            "desc": desc,
            "link": BASE_LINK + mail_handle
        })


def format_list(input_list):
    input_list.sort(key=lambda x: x["name"])
    return '\n'.join([FORMAT_ENTRY.format(**x) for x in input_list])

output = [HEADER]
for idf, name in (('main','General Mailinglists'), \
            ('coaches', 'Coaches Lists'),('team', "Team Lists")):
    output.append("""## %s """ % name)
    output.append(format_list(collection[idf]))
    

formatted = '\n'.join(output)
with open(args.filename, "w") as writer:
    writer.write(formatted)

print "written to %s" % args.filename
