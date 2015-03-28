# Set the STATIC_ROOT environment variable so our scripts know
# where they are supposed to store their outputs on our server.
import os, yaml
env = yaml.load(open("/home/ancfinder/environment.yaml"))
os.environ["STATIC_ROOT"] = env["STATIC_ROOT"]

# Run da scripts.
os.system(". .env/bin/activate; python scripts/scrape_anc.py")
os.system(". .env/bin/activate; python scripts/update_meeting_times.py")
