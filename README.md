# Cars Api

Api for management of your cars

## Prerequisites:

To install and run this project, you will need to set `SECRET_KEY` environmental variable in the
 your working shell. (Windows CLI: `set SECRET_KEY=<your_secret_key>` Unix CLI: `export SECRET_KEY=<your_secret_key>`)

The value of this variable is of your choice. Please, refer to Django docs for more info.

## Installation
```
git clone https://github.com/tkozuch/TalixoCars.git
cd ./TalixoCars
pip install -r requirements.txt
python ./cars_site/manage.py migrate
```

## Running tests:

```python ./cars_site/manage.py test cars_app```

## Running app:
```
python ./cars_site/manage.py runserver
```

App shall be available at:
http://127.0.0.1:8000/

### Available operations:

#### Add car:
```
POST http://127.0.0.1:8000/car:add

Headers:
    "Content-Type": "application/json"

Body: 
{
	"registration_number": "asdf-1323",
	"max_passengers": 33,
	"year_of_manufacture": 2000,
	"model": "Golf",
	"manufacturer": "Volkswagen",
	"category": "first class",
	"motor_type": "electric"
}
```

#### Update car: (only parameters to be changed need to be send)
```
POST http://127.0.0.1:8000/car:update

Headers:
    "Content-Type": "application/json"

Body: 
{
	"registration_number": "xxx",
	"pk": 4
}
```

#### Get car:
```
GET http://127.0.0.1:8000/car:retrieve

Params: 
    id <id of the car>
    show_category <[true/false] default:false, determines whether to fetch category property>
    show_motor_type <[true/false] default:false, determines whether to fetch category property>
```

#### Get cars list:

```
GET http://127.0.0.1:8000/car:list

Params: 
    max_passengers <int: show only cars with this many max passengers>
    max_passengers__gt <int: show only cars that have number of max passengers greater then>
    [...] # more parameters possible
    show_category <[true/false] default:false, determines whether to fetch category property>
    show_motor_type <[true/false] default:false, determines whether to fetch category property>

Example:
http://127.0.0.1:8000/car:list?show_category=True&max_passengers__gt=10&registration_number__icontains=x
```

#### Delete car:

```
POST http://127.0.0.1:8000/car:delete

Headers:
    "Content-Type": "application/json"

Body: 
{
	"pk": <int: identifier of Car to delete (also called "id")>
}
```


### Postman collection is available:

https://www.getpostman.com/collections/f558178721855be8ada7