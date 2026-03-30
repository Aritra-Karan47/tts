from resemble import Resemble

Resemble.api_key("3ZwpWy45B9oFreEFdZOCAQtt")

projects = Resemble.v2.projects.all(1, 10)
for p in projects['items']:
    print(f"Name: {p['name']}  |  UUID: {p['uuid']}")

from resemble import Resemble

Resemble.api_key("3ZwpWy45B9oFreEFdZOCAQtt")

voices = Resemble.v2.voices.all(1, 10)
for v in voices['items']:
    print(f"Name: {v['name']}  |  UUID: {v['uuid']}")