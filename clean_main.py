import subprocess

if __name__ == '__main__':
    res = subprocess.run(['docker', 'stop', 'some-rabbit'],
                         stdout=subprocess.PIPE)
    print('rabbitmq docker:')
    print(res.stdout)
