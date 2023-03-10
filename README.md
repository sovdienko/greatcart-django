
1. Create new project

```
django-admin startproject greatcart .
```

2. Run server

```
python manage.py runserver
```

3. Collect static (css, png, img, js ..) files

```
python manage.py collectstatic
```

4. Create app

```
python manage.py startapp category
```

5. Create database scripts

```
python manage.py makemigrations <app>
```

6. Run database scripts

```
python manage.py migrate

# to remove migration
python manage.py migrate --fake
```

7. Create django admin

```
python manage.py createsuperuser
```

8. GIT

gitignore.io - site for generation of .gitignore content for Django
```
git init
git add -A 
git commit -m "initial commit" 
```

9. Django AWS

```
https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/create-deploy-python-django.html
```