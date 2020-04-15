import subprocess

if __name__ == '__main__':
    res = subprocess.run(['docker', 'run', '--rm', '-d',
                          '--hostname', 'my-rabbit',
                          '-p', '5672:5672',
                          '-p', '5671:5671',
                          '-p', '15672:15672',
                          '-e', 'RABBITMQ_DEFAULT_VHOST=my_vhost',
                          '--name', 'some-rabbit',
                          'rabbitmq:3'], stdout=subprocess.PIPE)
    print('rabbitmq docker:')
    print(res.stdout)
    res = subprocess.run(['python', 'manage.py', 'runserver', '0.0.0.0:8080'],
                         stdout=subprocess.PIPE)
    print('django:')
    print(res.stdout)
