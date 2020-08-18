import requests
import json
import os

from argparse import ArgumentParser

from consts import CONFIG_FILE


class Github:
    def __init__(self, username: str, token: str):
        self.username = username
        self.token = token

        self.session = requests.Session()
        self.session.auth = (self.username, self.token)

        self.url = 'https://api.github.com'
    
    def verify(self):
        res = self.session.get(self.url)

        if res.status_code == 401:
            print('Bad credentials, please insert again.')
            return False
        else:
            return True

    def get_repos(self) -> list:
        res = self.session.get(f'{self.url}/user/repos')

        if res.status_code == 401:
            return False

        output = lambda repo: print(
            f'{"private" if repo["private"] else "public"} {repo["name"]}'
        )

        [
            output(repo)
            for repo in res.json()
        ]

    def create_repo(self, **kwargs):
        res = self.session.post(f'{self.url}/user/repos', json=kwargs)

        if res.status_code == 401:
            print('Bad credentials, please insert again.')
            return create_config()
        if res.status_code == 201:
            print(f'Repository {kwargs.get("name")} created successfully.')
            return True
        if res.status_code == 422:
            print(f'Name {kwargs.get("name")} already exists.')
        else:
            print('Sorry, an unexpected error occured, please try again later.')

    def delete_repo(self, name: str):
        res = self.session.delete(f'{self.url}/repos/{self.username}/{name}')

        if res.status_code == 204:
            print(f'Repository {name} deleted successfully.')
        else:
            print(f'Repository {name} not found.')

def erase_config():
    if os.path.isfile(CONFIG_FILE):
        os.remove(CONFIG_FILE)

def create_config():
    erase_config()

    valid = False

    while not valid:
        username = input('Username: ')
        token = input('Token: ')

        gh = Github(username, token)

        if gh.verify():
            valid = True
        else:
            print('\nBad credentials, please insert again.')

    with open(CONFIG_FILE, 'w+') as f:
        f.write(json.dumps({
            'username': username,
            'token': token
        }))

    os.chmod(CONFIG_FILE, 0o777)

    return { 'username': username, 'token': token }

def get_args():
    parser = ArgumentParser()

    parser.add_argument('op', metavar='operation', type=str, help='Operation type [create | delete]')
    parser.add_argument('name', metavar='name', type=str, help='Repository name', nargs='?')
    parser.add_argument('--desc', metavar='description', type=str, help='Repository description')
    parser.add_argument('--public', dest='public', help='Public mode', action='store_true')

    return parser.parse_args()

def main():
    args = get_args()

    if not args:
        return

    if os.path.isfile(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            configs = json.load(f)
    else:
        configs = create_config()
    
    gh = Github(configs['username'], configs['token'])
    
    if not gh.verify():
        erase_config()
        main()

    if args.op == 'create':
        gh.create_repo(name=args.name, description=args.desc, private=False if args.public else True)

    if args.op == 'delete':
        confirm = input(f'Are you sure you want to PERMANENTLY delete {args.name}? (y/n): ')
        if confirm == 'y':
            gh.delete_repo(name=args.name)
        else:
            return

    if args.op == 'list':
        gh.get_repos()

if __name__ == '__main__':
    main()
