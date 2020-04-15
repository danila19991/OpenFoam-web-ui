import subprocess

if __name__ == '__main__':
    res = subprocess.run(['python3', 'manage.py', 'makemigrations'],
                         stdout=subprocess.PIPE)
    print(res.stdout)
    res = subprocess.run(['python3', 'manage.py', 'makemigrations',
                          'auth_and_static'], stdout=subprocess.PIPE)
    print(res.stdout)
    res = subprocess.run(['python3', 'manage.py', 'makemigrations',
                          'task_controller'], stdout=subprocess.PIPE)
    print(res.stdout)
    res = subprocess.run(['python3', 'manage.py', 'migrate'],
                         stdout=subprocess.PIPE)
    print(res.stdout)
