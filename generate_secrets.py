import json
import os

with open("credentials.json", "r") as f:
    data = json.load(f)

data["private_key"] = data["private_key"].replace("\\n", "\n")
os.makedirs(".streamlit", exist_ok=True)

with open(".streamlit/secrets.toml", "w") as out:
    out.write("[gsheets]\n")
    for k, v in data.items():
        if isinstance(v, str):
            if k == "private_key":
                out.write(f'{k} = """{v}"""\n')
            else:
                out.write(f'{k} = "{v}"\n')

