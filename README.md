# Python-Postgres-Flask-App

A project in Python, SQLAlchemy(Postgres), and Flask

## How it works

1. HTTP requests and responses are handled by Flask web framework.
2. JSON Web Token is used to authenticate and authorize users.
3. SQLAlchemy with SQLite is used to store data.
4. Tornado is used as a web server.
5. Facebook and Google + OAuth 2.0 are used 

## Main dependencies
- [Python](https://www.python.org/) version 2.7.x or higher
- [Flask](http://flask.pocoo.org/) version 0.10.x or higher
- [Jinja2](http://jinja.pocoo.org/docs/dev/) 2.7.x or higher
- [SQLAlchemy](http://www.sqlalchemy.org/) 0.8.x or higher
- [PyJWT](https://github.com/jpadilla/pyjwt) 1.3.x or higher
- [Tornado](http://www.tornadoweb.org/en/stable/) 4.x or higher
- [Oauth2.0client](https://developers.google.com/api-client-library/python/guide/aaa_oauth) 1.4.x or higher 


## Getting Started

### Setting the basic environment (Ubuntu 14.04)
```bash
sudo apt-get install build-essential
sudo apt-get install update
sudo apt-get install upgrade
sudo apt-get install ufw git apache2 libapache2-mod-wsgi python-dev python-setuptools python-pip

```
### Setting the front-end environment
```bash
sudo apt-get install nodejs
sudo apt-get install npm
npm install -g bower

```

### Setting Postgres SQL
```bash
sudo apt-get install libpq-dev
sudo apt-get install postgresql postgresql-contrib
```

### Create a new user
```bash
adduser new-user-name
```

give the user sudo previliges

```bash
sudo adduser new-user-name sudo
```


### Change the SSH port
Edit ssh configuration ```nano /etc/ssh/sshd_config``` and edit below:
```bash
Port 22 -> Port 2200
AllowUsers root new-user-name
```

run ```service ssh restart``` to apply the changes.


### Configure the Uncomplicated Firewall
```bash
ufw enable
sudo ufw allow 80/tcp
sudo ufw allow 2200
sudo ufw allow 123/ntp
```


### Cloning the source code.
Make source folder
```bash
cd /var/www
git clone https://github.com/SsureyMoon/Python-Postgres-Flask-App.git
mv Python-Postgres-Flask-App catalog_app
```


### Configurating Apache2
Configure wsgi
```bash
sudo a2enmod wsgi
sudo nano /etc/apache2/sites-available/catalog_app.conf
```

In ```/etc/apache2/sites-available/catalog_app.conf```:
```
<VirtualHost *:80>
                WSGIDaemonProcess catalog_app python-path=/var/www/catalog_app:$
                WSGIProcessGroup catalog_app
                WSGIScriptAlias /catalog /var/www/catalog_app/catalog_app.wsgi
                <Directory /var/www/catalog_app/>
                        Order allow,deny
                        Allow from all
                </Directory>
                ErrorLog ${APACHE_LOG_DIR}/error.log
                LogLevel warn
                CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
```

Register wsgi module
```bash
sudo a2ensite catalog_app
sudo nano /etc/apache2/sites-available/catalog_app.conf
```

Restart Apache2
```bash
service apache2 restart
```


### Installing python dependencies
Make virtual environment
```bash
cd /var/www/catalog_app
sudo pip install virtualenv 
sudo virtualenv catalog_venv
source catalog_venv/bin/activate
```

Backend dependencies

```bash
cd /var/www/catalog_app
pip install -r requirements.txt
```

Frontend dependencies
```bash
cd /var/www/catalog_app/catalog_app
npm install -g bower
ln -s /usr/bin/nodejs /usr/bin/node
bower update --allow-root
```

### Downloading a credentials file for Google + OAuth
For Google Plus Oauth, we need to download google api credential file.
Visit your developer console and downlaod credentials.json.
The ```url``` must look like this:

https://console.developers.google.com/project/**your-app-name**/apiui/credential

Place the ```client_secret.json``` file downloaded in the folder ```catalog_app/settings/```

### Setting credentials for Facebook OAuth
Open ```/var/www/catalog_app/settings/config.py```, find these lines:
```python
# Replace this with your facebook client id.
FACEBOOK_CLIENT_ID = ""
# Replace this with your facebook client secret.
FACEBOOK_CLIENT_SECRET = ""
```
Visit your Facebook developer page and go to the settings tab.
The ```url``` must look like this:

https://developers.facebook.com/apps/**your-app-id**/settings/basic/
Find ```App ID``` and ```App Secret``` and fill the blanks inthe ```catalog_app/settings/config.py```

** Please NEVER commit your code with your app secret! You can avoid that by running this command: **
```bash
cd /var/www/catalog_app
echo 'settings/config.py' >> .gitignore
```

### Creating database
```bash
sudo -i -u postgres
postgres=# \password
Enter new password: 
Enter it again:
postgres=#
```
Importing dummy data
```bash
cd /var/www/catalog_app
python testdata.py
```
Now, we can login with username: user{i}@email.com, password: user{i}password.
For example, username: ```user1@email.com```, password: ```user1password```

## Test the server
Test your application by visiting http://52.11.89.94