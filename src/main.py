import requests
import json
import os

from argparse import ArgumentParser


class Github:
    def __init__(self, username: str, token: str):
        self.session = requests.Session()
        self.session.auth = (username, token)

        self.url = 'https://api.github.com'
    
    def get_repos(self) -> list:
        repos = self.session.get(f'{self.url}/user/repos')

        return [repo['name'] for repo in repos.json()]

    def create_repo(self, **kwargs):
        res = self.session.post(f'{self.url}/user/repos', json=kwargs)

        if res.status_code == 201:
            print('Success.')
        else:
            print('Error.')
        
def create_config(config_file: str):
    username = input('Username: ')
    token = input('Token: ')

    with open(config_file, 'w+') as f:
        f.write(json.dumps({
            'username': username,
            'token': token
        }))

    os.chmod(config_file, 0o777)

    return { 'username': username, 'token': token }

def main():
    config_file = 'gipconf.json'

    if os.path.isfile(config_file):
        with open(config_file, 'r') as f:
            configs = json.load(f)
    else:
        configs = create_config(config_file)
        
    gh = Github(configs['username'], configs['token'])

if __name__ == '__main__':
    main()