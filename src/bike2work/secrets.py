import dotenv
import os


home_dir = os.path.expanduser("~")
env_file = os.path.join(home_dir, '.bike2work.env')

dotenv.load_dotenv(env_file)

maps_key = os.getenv("MAPS_API_KEY")

if not maps_key:
    print("""
    No MAPS_API_KEY found. Either set the environment variable MAPS_API_KEY or create a file at ~/.bike2work.env with the following contents:
    
    MAPS_API_KEY=YOUR_API_KEY_HERE
    """)
    raise Exception("No API key found")