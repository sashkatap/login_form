# Simple login form create with Python + FastAPI

server.py The simplest testing authentication server, written in FastAPI.

This is my practice project for the course "Computer and Web Technologies Fundamentals with Python from Digitalize".
This allows us to receive form data, cookies and an encrypted password. Check the password and if it's valid, authorize the user, greet him and show his balance.

It hasn't logout button yet, so to logout clear cookie (in browser F12 and write down in Console: `document.cookie = 'username='` ).

## It works on VPS with Nginx < Guvicorn < Uvicorn < Python code

Requirements: Python3.9.7, FastAPI.

## Installation on VPS:

1. Install Python 3.9.7
2. Install nginx server
3. Install git
4. `$ git clone git@github.com:sashkatap/login_form.git`
5. create venv, activate `$ python3.9 -m venv env` & `$ ../env/bin/activate`
6. pip install -r pip_requirement.txt
7. `$ uvicorn server:app --reload`
8. configure nginx to redirect all requests to uvicorn:

To make that create a conf file to: etc/nginx/site-enabled/login_form.conf

```
server {
    server_name DomainName.ru;
    location / {
        include proxy_params;
        proxy_pass http://127.0.0.1:8000;
    }
}
```

In this code replace `DomainName.ru` to your real domain name.

9. install gunicorn (as a process manager for using all processor cores)
10. make automation service to start the server, if it's down

For that make a conf file to: etc/systemd/system/login_form.service

```
[Unit]
Description=Gunicorn instance to serve login_form app
After=network.target

[Service]
User=UserName
Group=GroupUserName
WorkingDirectory=/home/UserName/login_form
Environment="PATH=/home/UserName/login_form/env/bin"
ExecStart=/home/UserName/login_form/env/bin/gunicorn -w 5 -k uvicorn.workers.UvicornWorker server:app

[Install]
WantedBy=multi-user.target
```

Replase `UserName` and `GroupUserName` to your server user name and user group!

11. restart nginx
12. activate and start the service:

`$ systemctl enable login_form`  
`$ systemctl start login_form`

13. install several necessary modules:

`$ pip install uvloop`  
`$ pip install httptools`

14. check the service work `$ systemctl status login_form`
    <br />
    <br />

### Test:

Open your domain insted off `DomainName.ru` and enter:

login `alex@user.com`

password `some_password_1`

It works correctly, if you see your balance: 100 000
