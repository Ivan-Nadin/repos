
import argparse
parser = argparse.ArgumentParser(description='Launch telegram bot')
parser.add_argument('token', type=str, help='Authentication token for bot')
parser.add_argument('user', type=str, default='postgres',help='User for connecting to Postgres Database')
parser.add_argument('password', type=str, default='1',help='Password for connecting to Postgres Database')
parser.add_argument('--host', type=str, default='localhost',help='Host for launching Postgres Database')
parser.add_argument('--port', type=str, default='5432',help='Port for launching Postgres Database')
parser.add_argument('--database', type=str,default='postgres' , help='Name of connecting Postgres Database')
args = parser.parse_args()
print(args.token)
