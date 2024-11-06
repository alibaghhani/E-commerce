
# Restful E-commerce project

The RESTful E-Commerce Application is a robust web platform developed using Django that enables users to buy and sell products online. This application provides features such as user authentication, product management, a shopping cart, and a secure checkout process. The project adheres to RESTful principles, making it easy to integrate with front-end frameworks or mobile applications. It aims to deliver a seamless shopping experience, equipped with a comprehensive admin panel for managing products, orders, and users effectively.



## Run Locally

Clone the project

```bash
  git clone git@github.com:alibaghhani/E-commerce.git
```

Go to the project directory

```bash
  cd E-commerce/
```

open terminal and create your own env file

```bash
  python3 -m venv venv 
```
note: you can set anything for env file's name but
venv is suggested. 
for more information visit [venv 🔗](https://docs.python.org/3/tutorial/venv.html#creating-virtual-environments)


activate venv

```bash
  source venv/bin/activate
```

install requirements

```bash
    pip install requirements.txt
```

you should use your own secret_key and db configuration. for secret_key you can visit [secrey_key generator 🔗](https://djecrety.ir/)

check **[env.example](https://github.com/alibaghhani/E-commerce/blob/main/env.example)** file and config it based on your configuration

migrate db 

```bash
python3 manage.py migrate
```

run django server

```bash
python3 manage.py runserver
```




## Authors

- [@alibaghhani](https://github.com/alibaghhani/)


## Deployment

To deploy this project with docker 

```bash
  docker-compose up --build 
```


## Feedback

If you have any feedback, please reach out to us at baghaniali2006@gmail.com


## Features

- **Basket Management with Redis**: This feature allows users to manage their shopping basket in real-time using Redis, providing fast and efficient operations for adding/removing items, updating quantities, and applying discounts.


## Acknowledgements

 
 - [How to generate README](https://readme.so/editor)
 - [How to write a Good readme](https://bulldogjob.com/news/449-how-to-write-a-good-readme-for-your-github-project)


## Environment Variables

To run this project, you will need to add the following environment variables to your .env file

`SECRET_KEY`

`Postgresql database settings`

`Redis databse settings`

please check **env.example** for more information about environment variables.


## 🚀 About Me
I'm a backend developer...


## License

[MIT](https://choosealicense.com/licenses/mit/)

**Main Database**  [Postgresql](https://www.postgresql.org/)

**Second Database** [Redis](https://redis.io/)

**Caching** [Redis](https://redis.io/)

**Web Server** [Gunicorn](https://gunicorn.org/)

**Reverse Proxy** [Nginx](https://nginx.org/en/)

