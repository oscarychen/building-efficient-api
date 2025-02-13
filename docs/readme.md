# Building efficient maintainable REST APIs for data retrieval
_comparing methodologies in Django REST Framework, Django-Ninja, and Golang_


In this repo, I have set up multiple mini projects to compare how different API code designs can affect performance.

We start with a simple toy example of a **Django REST Framework API**, we will add a bit requirement to the API and see that it struggles to return 100k rows in over 30 seconds, and then step-by-step optimize it to return in under 1 second.

I've also set up an identical API using **Django-Ninja**, as well as using **Golang** with **sqlc** and **mux**, to compare their performances.

Jump to TLDR [Conclusions](#conclusions-tldr)


# Data model

For this experiment, we will set up small data models in each tech stack:

```
+------------+              +------------+
|     Car    |              |  CarModel  |
+------------+              +------------+
|  model_id  | -----------> |     id     |
+------------+              +------------+
```

The Car and CarModel models have 1-to-many relationship between them, each with some of their own attributes not shown in the diagram.

## Part A: Django REST Framework (DRF)

Django is a popular choice for startups and hobby projects. It offers a feature-rich ORM and migration system. Django REST Framework is widely used for building web application backends with Django.
To get started, I've included some basic docker configuration for Django development server and postgres server, as well as a simple management command to populate 100k rows of Car records.
- build: `make docker-build`
- run Django REST Framework: `make docker-up-drf`
- run Django-Ninja: `make docker-up-ninja`
- run Go: `make docker-up-go`
- populate database with 100k Car records: `make django-drf-populate`

### Chapter 1: Retrieving Car records Using DRF ModelSerializer

In typical Django REST framework toy example fashion, we set up a ModelSerializer and API View as such:

```python
# django_drf/car_registry/serializers.py
class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = '__all__'

# django_drf/car_registry/views.py
class CarListView(ListAPIView):
    serializer_class = CarSerializer
    queryset = Car.objects.all()
```

and expose this API View as on the follow route:

```python
# django_drf/config/urls.py
urlpatterns = [
    path('cars/', CarListView.as_view()),
    ...
]
```

Now, we can hit this endpoint (you can use the api.http file provided in the repository root)

> GET http://localhost:8000/cars/

> Response code: 200 (OK); Time: 2564ms (2 s 564 ms); Content length: 15107465 bytes (15.11 MB)

### Chapter 2: Retrieving Car records with related model attributes using DRF ModelSerializer

Next, we are going to want to return some additional data for each of the Car record retrieved while maintaining the response data structure, particular the related CarModel's attributes `name`, `year`, and `color`. Most Django developers would simply make the following changes to the serializer:

```python
# django_drf/car_registry/serializers.py
class CarSerializerWithRelatedModel(serializers.ModelSerializer):
    car_model_id = serializers.IntegerField(source='model_id', read_only=True)
    car_model_name = serializers.CharField(source='model.name', read_only=True)
    car_model_year = serializers.IntegerField(source='model.year', read_only=True)
    color = serializers.CharField(source='model.color', read_only=True)
    class Meta:
        model = Car
        fields = ...
```

For comparison purpose, we keep the original API as-is, and added the modified API as a new API. Now we hit this new endpoint

> GET http://localhost:8000/retrieve-cars-with-model/

> Response code: 200 (OK); Time: 30779ms (30 s 779 ms); Content length: 22856443 bytes (22.86 MB)

That took a lot longer.
The query in the API view `Car.objects.all()` did not contain data about each `Car` record's related `CarModel` record, by the time the Serializer is trying to serialize each record, Django has to fire off an additional query to fetch the related `CarModel` in order to get the `model_name`, `model_year` and `color` that the serializer is asking for. This is called N+1 query problem, and it's very common problem in stacks involving some sort of ORM.

In Django REST Framework, this can be a very easy mistake to make (simply by modifying a serializer) and sometimes not easy to spot; luckily it's usually pretty simple to fix.

### Chapter 3: Optimizing retrieving Car records with related model attributes using query Select_related / Prefetch_related

Based on the previous example, we are going to modify the query by "prefetching" the related records:

```python
# django_drf/car_registry/views.py
class CarListViewWithModelPrefetched(ListAPIView):
    serializer_class = CarSerializerWithRelatedModel
    queryset = Car.objects.all().select_related('model')  # or .prefetch_related('model')
```

Again, for comparison purpose, we keep the previous API as-is, and added the modified API as a new API. Now we hit this new endpoint

> GET http://localhost:8000/retrieve-cars-with-prefetch-related/

> Response code: 200 (OK); Time: 3968ms (3 s 968 ms); Content length: 22856443 bytes (22.86 MB)

Now we are back down to around 3 seconds.

The `prefetch_related('model')` tells to the ORM to perform a single query to fetch all the related `CarModel` model instances, and the returned data from database contains all the attributes of `CarModel`, so when the serializer tries to access those attributes, the ORM does not need to query the database again, thus the N+1 query problem is eliminated.
The `select_related('model')` performs a SQL join on the original SQL query as long as the relation is not a many-to-many relation, and the SQL query result contains the related data in a single query, and is technically preferred in our example here.

This is typically where most Django REST Framework application would stop at in terms of API query optimization. However, sometimes we are requesting so much data, this is still not enough. But first, let's re-organize our project structure a little bit.

### Chapter 4: Digress - Changing up the project structure a bit

We are going to leave the previous implemented serializers.py and views.py where they are for now even though we will not be using them anymore.

We want a project with 3 tiers: Models, Services, and APIs. Service and API code will be outside the Django app directory, while Django app directories will store models. This setup allows us to develop services that can encapsulate complex business logic using multiple models and across different Django apps if needed.

```
/django_project_root
|-/project_level_config
|-/apis
| |-/some_api.py
| |-/some_other_api.py
|-/services
| |-/feature_a_services.py
| |-/feature_b_services.py
| |-...
|-/app_1
| |--/app_1_models.py
|-/app_2
| |--/app_2_models.py
|-...
```

I also do not like separating Serializer implementation from the API View implementation. Saving a bit of code duplication but create coupling between serializers and therefore APIs can be a source of problem in larger teams. As you have seen previously, it's very easy for a developer to make a little change in 1 serializer and somehow causes performance problems in serializers and views elsewhere. I would put the serializer and the view implementation together in a `some_api.py`, in fact I would put request param serializer, request body data serializer, and response serializer implementation all in the same file with the API View implementation that they are responsible for.

You could probably also put all the Django app modules in a repository directory. In a way we are opinionated to use Django mostly only as a Model Repository, and we want to manage rest of the Django project structure ourselves more or less in a different pattern. But we won't go that far.

With these in mind, we are going to implement the following:

```python
# django_drf/services/car_services.py
class CarService:
    def retrieve_all_cars(self):
        pass

# django_drf/apis/car_listing_api.py
class CarListingAPI(APIView):
    def get(self, *args, **kwargs) -> Response:
        return Response({'detail': 'to be implemented'}, status=status.HTTP_501_NOT_IMPLEMENTED)
```

Now we are ready to flesh out some of the implementation details next.

### Chapter 5: Replacing ModelSerializer with Serializer

The first thing we are going to try is to use a DRF Serializer instead of ModelSerializer. Serializers are lighter weight than Model Serializer, while ModelSerializer automatically creates field-level validators from their corresponding Model's field validators and simplifies write operations, it's an unnecessary overhead for read operations like listing and retrieving records from the database.

We are going to fill out the service and API from the previous section as the following:

```python
# django_drf/services/car_services.py
class CarService:
    def retrieve_all_cars(self):
        return Car.objects.all().select_related('model')
    
# django_drf/apis/car_listing_api.py
class CarListingResponseSerializer(serializers.Serializer):
    vin = serializers.CharField()
    owner = serializers.CharField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    model = serializers.IntegerField(source="model_id")
    model_name = serializers.CharField(source='model.name')
    model_year = serializers.IntegerField(source='model.year')
    color = serializers.CharField(source='model.color')
    
class CarListingAPI(APIView):
    def get(self, *args, **kwargs) -> Response:
        car_instances = CarService().retrieve_all_cars()
        response_serializer = CarListingResponseSerializer(car_instances, many=True)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
```
Now we hit this new endpoint
> GET http://localhost:8000/api/cars/

> Response code: 200 (OK); Time: 3996ms (3 s 996 ms); Content length: 22856443 bytes (22.86 MB)

This is not really faster than previous implementation. The DRF Serializer is still iterating through each of the Car instances to turn it into a Python dictionary. There are few other things you can try here in Python to speed up the process, but we are going to move onto something else.

### Chapter 6: Using Django ORM more and DRF Serializer less
Next we are going to write the query in a way that we can get the data we want directly from the database, so that we can skip turning the data into Python dictionaries before serializing them into json.

Building on the existing CarService class:
```python
# django_drf/services/car_services.py
class CarService:
    def retrieve_all_cars(self):
        return Car.objects.all().select_related('model')

    def retrieve_all_cars_annotated(self):
        qs = self.retrieve_all_cars()
        qs = qs.annotate(
            car_model_id=F('model_id'),
            car_model_name=F('model__name'),
            car_model_year=F('model__year'),
            color=F('model__color')
        )
        return qs

    def retrieve_all_cars_as_dicts(self):
        cars = self.retrieve_all_cars_annotated()
        return cars.values(
            'id',
            'vin',
            'owner',
            'created_at',
            'updated_at',
            'car_model_id',
            'car_model_name',
            'car_model_year',
            'color'
        )
```
Here we try to leverage the database as much as possible to produce the final data as closely as we would want to return through the API.
We will implement the API as follows:
```python
# django_drf/apis/car_listing_api_2.py
class CarListingAPI(APIView):
    def get(self, *args, **kwargs) -> Response:
        car_dicts = CarService().retrieve_all_cars_as_dicts()
        return Response(car_dicts, status=status.HTTP_200_OK)
```
For comparison purpose, again we keep the original API as-is, and added the modified API as a new API.
Now we hit this new endpoint

> GET http://localhost:8000/api/cars-2/

> Response code: 200 (OK); Time: 1373ms (1 s 373 ms); Content length: 22856443 bytes (22.86 MB)

There we cut the time in half again, mostly because we are not iterating the N number of Car instances in Python from the queryset as it is already serializeable.
This is not always possible and sometimes may require you to write some pretty complicated Django queries. But as long as there is a way to write the query and make the database do the work, it's probably going to be faster than doing it in Python.

### Chapter 7: Faster serialization using OrJson
The last thing we are going to try to use a faster JSON serializer. Django REST Framework uses Python's built-in JSON serializer, which is not the fastest JSON serializer out there. We are going to use orjson, which is a fast JSON serializer written in Rust.

First, we implement a custom response class that uses orjson to serialize the response data:

```python
# django_drf/custom_response.py
class OrJsonResponse(HttpResponse):
    def __init__(self, data, json_dumps_params=None, *args, **kwargs):
        if json_dumps_params is None:
            json_dumps_params = {}
        kwargs.setdefault("content_type", "application/json")
        if isinstance(data, QuerySet):
            data = list(data)
        data = orjson.dumps(data, **json_dumps_params)
        super().__init__(content=data, **kwargs)
```

With that in place, lets implement the previous API but returns the response using OrJsonResponse:

```python
# django_drf/apis/car_listing_api_3.py
class CarListingAPI(APIView):
    def get(self, request: Request, *args, **kwargs) -> Response:
        car_dicts = CarService().retrieve_all_cars_as_dicts()
        return OrJsonResponse(car_dicts, status=status.HTTP_200_OK)
```
Finally, we hit the new endpoint that uses OrJsonResponse

> GET http://localhost:8000/api/cars-3/

> Response code: 200 (OK); Time: 1035ms (1 s 35 ms); Content length: 23856443 bytes (23.86 MB)

And now we are able to get this API to return in about 1 second with 100k records with data from two tables.

### Chapter 8: Other performance considerations
At this point we have optimized the API from database query to response serialization. There are still some other areas that would affect API performance:
- database indexing: It is likely that you would have some sort of filtering in the query, which means you need to consider database indexing. You would want to design your services in a way that they can take the parsed query parameters and use them for filtering as part of the Django query, and avoid doing any sort of filtering in Python.
- query caching: generally a good idea especially if the data is relatively static
- web server compression: such as gzip, would compress the response data to be magnitudes smaller especially for large responses like the example used here

### Chapter 9: Pagination
By this point, you probably are wondering why we are not using pagination. I don't think pagination is strictly a performance optimization as it requires a different design in the API consumer (frontend app) which sometimes result in a different user experience requirement. Nevertheless, it is easy enough to add the Pagination class from DRF:
```python
# django_drf/apis/car_listing_api_4_paginated.py
class CarListingAPI(APIView):
    def get(self, request: Request, *args, **kwargs) -> OrJsonResponse:
        car_dicts = CarService().retrieve_all_cars_as_dicts()
        paginator = PageNumberPagination()
        paginated_car_dicts = paginator.paginate_queryset(car_dicts, request)
        return OrJsonResponse(paginated_car_dicts, status=status.HTTP_200_OK)
```
In the django settings, I set the page size to be 1000, and hit the new endpoint
> GET http://localhost:8000/api/cars-4-paginated/?page=4

> Response code: 200 (OK); Time: 65ms (65 ms); Content length: 238164 bytes (238.16 kB)

As expected, the response is much smaller and faster to return.

## Part B: Django-Ninja

Django-Ninja is a newer API framework that is built on top of Django and Pydantic. It is designed to be faster than Django REST Framework, and has similar syntax to FastAPI.
I'm going to copy the django_drf project and modify it to use Django-Ninja instead of Django REST Framework.
The new ninja-powered Django project is set up in its own docker container and exposed on port 8001.

### Chapter 1: Retrieving Car records Using Ninja API
Similar to how we have previously set up the Django REST Framework API, we are going to set up a Ninja API in django_ninja/apis/:
```python
# django_ninja/apis/car_listing_api.py
class ListCarResponseItem(Schema):
    vin: str
    owner: str
    created_at: datetime
    updated_at: datetime
    car_model_id: int
    car_model_name: str
    car_model_year: int
    color: str

@router.get("/cars/", response=list[ListCarResponseItem])
def list_cars(request: HttpRequest):
    return CarService().retrieve_all_cars_annotated()
```
The Ninja Schemas are analogous to Django REST Framework Serializers, and defines the API's request and response data structure.
Note that this API is making use of the previously implemented CarService method `retrieve_all_cars_annotated`, so this example is comparable to Part A Chapter 5 example.

Now we hit this new endpoint
> GET http://localhost:8001/ninja/with-schema/

> Response code: 200 (OK); Time: 3602ms (3 s 602 ms); Content length: 23856443 bytes (23.86 MB)

This is comparable performance to the Django REST Framework implementation using Serializer with CarService's annotated queryset (Part A Chapter 5), I suspect that there is no significant performance advantage using the Ninja Schema over DRF Serializer since both are converting ORM objects in Python.


### Chapter 2: Returning data directly from the database
Similar to Part A Chapter 6, we are going to try to return the data directly from the database without converting the ORM objects into Python dictionaries:
```python
@router.get("/cars-2/")
# django_ninja/apis/car_listing_api.py
def list_cars_2(request: HttpRequest):
    return list(CarService().retrieve_all_cars_as_dicts())
```
Now we hit this new endpoint
> GET http://localhost:8001/ninja/without-schema/

> Response code: 200 (OK); Time: 1367ms (1 s 367 ms); Content length: 24056442 bytes (24.06 MB)

Again, we cut down the time in half by not converting the ORM objects into Python dictionaries before serializing them into json. This is also comparable performance to the Django REST Framework implementation using CarService (Part A Chapter 6).

### Chapter 3: Using OrJson
Similar to Part A Chapter 7 of DRF, we are going to try to use OrJson to serialize the response data. Based on the Django-nina documentation, we implement an OrJSONRenderer:

```python
# django_ninja/custom_renderer.py
class ORJSONRenderer(BaseRenderer):
    media_type = "application/json"

    def render(self, request, data, *, response_status):
        return orjson.dumps(data)
```

and we add the renderer argument to the NinjaAPI instance:
```python
# django_ninja/config/urls.py
api = NinjaAPI(renderer=ORJSONRenderer())
```
We hit the endpoint implemented in previous chapter
> GET http://localhost:8001/orjson-api/cars/

> Response code: 200 (OK); Time: 1061ms (1 s 61 ms); Content length: 23856443 bytes (23.86 MB)

The performance is similar to the Django REST Framework implementation using OrJsonResponse (Part A Chapter 7).

## Part C: Golang with sqlc and mux

Finally, we are going to implement the same API using Golang. We are going to use sqlc to generate the database query code, and mux as the web server router. This is one of the more "bare metal" sort of approach to writing Go web server, and it does not involve any ORM.

The way sqlc works is that you write a SQL query in a .sql file, and sqlc generates Go code that can execute the query and scan the result into a struct. This is similar to how Django's ORM works, but sqlc is much more lightweight and does not have the same level of abstraction as Django's ORM.

To make things easier to set up, I'm going to "re-engineer" the Django models and put them into Go. Django has a command that allows you to see the SQL query generated for a migration:
```bash
docker exec -it api-demo-django-drf python manage.py sqlmigrate car_registry 0001 
```
And we copy the SQL query into `go_sqlc_mux/schemas/0001_initial.up.sql`.

This file is essentially a migration step that would be used to make changes to the database.

Similarly, we can steal the SQL query Django used by our previous CarService method `retrieve_all_cars_annotated`, you can simply put a breakpoint or print statement
after each query to see what SQL Django generated, ie: `print(str(qs.query))`.

We would put such query into `go_sqlc_mux/sqlc/queries/car_registry.sql`.

Next, we run `sqlc generate` to generate the go Repository code. These code will be in the `go_sqlc_mux/internal/repository/` folder. 
Inside of this folder you will see that sqlc has created database models `CarRegistryCar` and `CarRegistryCarmodel` as Go structs, that are akin to models we had set up in Django previously.

After implementing the Service and Transport layers, and a bunch of other rather verbose almost boilerplate setups, the API is complete. I have the Go server exposed on port 8080.

> GET http://localhost:8003/go/

> Response code: 200 (OK); Time: 486ms (486 ms); Content length: 22834258 bytes (22.83 MB)

Unsurprisingly, the Go implementation is the fastest yet.


# Part D: Comparison

Previously in Part A, we populated the database with 100k rows of records using the Django management command `make django-drf-populate`. Each time this command is run it adds another 100k records. Let add more data and see how Django REST Framework, Django-Ninja, and Golang compare.

For comparison purpose, I'm going to add an API that uses Django REST Framework's Serializer (Part A Chapter 5) and with returning the response using ORJson (Part A Chapter 7), so it can be a fair comparison against using Ninja's Schema and ORJson renderer (Part B Chapter 1/3).

For each data size, each API is tested 10 times, and the response time is recorded, the highest container memory usage during these 10 tests is also recorded. 5 of APIs implemented previously are part of this comparison:
- API implemented using Django REST Framework Serializer and OrJsonResponse
- API implemented using Django REST Framework without Serializer and OrJsonResponse
- API implemented using Django-Ninja Schema and ORJSONRenderer
- API implemented using Django-Ninja without Schema and ORJSONRenderer
- Go API implemented using mux and sqlc

The data sizes used for testing are as the following:
- 100k records, 23 MB uncompressed response data size
- 200k records, 46 MB uncompressed response data size
- 300k records, 69 MB uncompressed response data size
- 400k records, 92 MB uncompressed response data size

### Average response time in milliseconds

|                        | 100k records | 200k records | 300k records | 400k records |
|------------------------|--------------|--------------|--------------|--------------|
| DRF with Serializer    | 3750         | 7832         | 11235        | 14939        |
| Ninja with Schema      | 3455         | 6804         | 10148        | 13309        |
| DRF without Serializer | 1034         | 1929         | 2947         | 3529         |
| Ninja without Schema   | 947          | 1850         | 2739         | 3526         |
| Go with mux            | 504          | 904          | 1231         | 1716         |

![API response times charted](assets/api_response_times.png)

While Django REST Framework's Serializer and Django-Ninja's Schema are very expensive, Django-Ninja is overall faster and more memory efficient than Django REST Framework. Go is the fastest by a good margin. See appendix for test detail data.


### Docker container peak memory usage in MB during API request		

The memory usage below are observed during any of the test of a particular API, and average memory usage may be lower. This these numbers may be safer for sizing server requirements.
One thing that stood out to me was that Django REST Framework don't tend to release memory after the request is done, ie: the resting state memory usage appear to be often closer to the peak memory usage even when there is not request being processed. 
This could have server sizing implications, because in real world a server would not be handling just one request at a time, and the memory usage would be cumulative.

|                        | 100k records | 200k records | 300k records | 400k records |
|------------------------|--------------|--------------|--------------|--------------|
| DRF with Serializer    | 430          | 750          | 1060         | 1430         |
| Ninja with Schema      | 400          | 780          | 1145         | 1380         |
| DRF without Serializer | 310          | 430          | 515          | 655          |
| Ninja without Schema   | 160          | 340          | 380          | 580          |
| Go with mux            | 140          | 300          | 500          | 620          |

![API memory usage charted](assets/api_container_memory_peak.png)

Surprisingly, when Ninja is used without the Schema, it is as memory efficient and even more so than Go in some cases.


# Conclusions (TLDR)

### DRF Serializer and Ninja Schema are very expensive
Serializer from Django REST Framework and Schema from Ninja are Python implementation that helps to convert data and object on a per-record basis, for this reason when dealing with large dataset, they can be very slow.
Personally I think they are great for validating and sanitizing user input data during WRITE operations, but for READ operations, they are not always necessary and can be a performance bottleneck.

Using them as a way of accessing relations can also introduce N+1 query problem very easily as seen in Part A Chapter 2 example.

### Ninja is overall faster and more memory efficient than Django REST Framework
When comparing the APIs that implements DRF Serializer and Ninja Schema, Ninja appears to provide 8-13% performance improvement, while using about the same amount of memory.
When comparing the APIs that do not implement Serializer and Schema, Ninja appears to provide up to 8% performance improvement, while using 10-50% less memory; and is even comparable to API set up in Go in some cases.

### Go is the fastest
Being lightweight (no ORM), compiled, and statically typed, Go is the fastest and in most cases the most memory efficient implementation tested. 

However, without many of the tools Django provides out of the box, it can be more difficult to get a project set up and running.
In particular, I miss Django's ORM for writing simple queries, migrations, centralized settings, and ready-to-use authentication systems and various standard middlewares.
If you are interested, I have set up a [template Go web project](https://github.com/oscarychen/eau-de-go) structure that I think is maintainable and scalable, with some of the typical web backend features you would expect from Django.

# Appendix: test data

## 100k records retrieval test
 API response times in milliseconds

| DRF with Serializer | Ninja with Schema | DRF without Serializer | Ninja without Schema | Go with mux |
|---------------------|-------------------|------------------------|----------------------|-------------|
| 3727                | 3531              | 1226                   | 972                  | 623         |
| 3667                | 3336              | 1205                   | 1014                 | 442         |
| 3987                | 3697              | 947                    | 948                  | 549         |
| 3761                | 3326              | 1012                   | 897                  | 512         |
| 3939                | 3434              | 929                    | 913                  | 468         |
| 3597                | 3304              | 981                    | 961                  | 458         |
| 3702                | 3592              | 1134                   | 935                  | 455         |
| 3872                | 3528              | 950                    | 928                  | 463         |
| 3606                | 3390              | 1002                   | 945                  | 639         |
| 3644                | 3409              | 951                    | 952                  | 429         |


## 200k records retrieval test
 API response times in milliseconds

| DRF with Serializer | Ninja with Schema | DRF without Serializer | Ninja without Schema | Go with mux |
|---------------------|-------------------|------------------------|----------------------|-------------|
| 7913                | 6837              | 1876                   | 1802                 | 922         |
| 7679                | 6920              | 1916                   | 1898                 | 941         |
| 8085                | 6753              | 1955                   | 1816                 | 1058        |
| 7954                | 6679              | 2279                   | 1841                 | 790         |
| 7418                | 6833              | 1881                   | 1821                 | 959         |
| 7846                | 6728              | 1916                   | 1844                 | 811         |
| 7387                | 6588              | 1881                   | 1828                 | 904         |
| 7921                | 7224              | 1879                   | 1821                 | 941         |
| 7871                | 6636              | 1821                   | 1983                 | 872         |
| 8247                | 6840              | 1887                   | 1848                 | 840         |


## 300k records retrieval test
 API response times in milliseconds
 
| DRF with Serializer | Ninja with Schema | DRF without Serializer | Ninja without Schema | Go with mux |
|---------------------|-------------------|------------------------|----------------------|-------------|
| 11417               | 10634             | 2984                   | 2741                 | 1277        |
| 11129               | 9907              | 2942                   | 2858                 | 1241        |
| 11184               | 10113             | 2957                   | 2750                 | 1119        |
| 11306               | 10201             | 2924                   | 2733                 | 1274        |
| 11333               | 9831              | 2954                   | 2725                 | 1222        |
| 11229               | 10274             | 2973                   | 2755                 | 1309        |
| 11197               | 10022             | 2915                   | 2689                 | 1141        |
| 11157               | 10056             | 2924                   | 2729                 | 1210        |
| 11200               | 10188             | 2996                   | 2701                 | 1161        |
| 11196               | 10254             | 2896                   | 2709                 | 1358        |


## 400k records retrieval test
 API response times in milliseconds
 
| DRF with Serializer | Ninja with Schema | DRF without Serializer | Ninja without Schema | Go with mux |
|---------------------|-------------------|------------------------|----------------------|-------------|
| 15668               | 13421             | 3508                   | 3475                 | 1824        |
| 15051               | 13210             | 3563                   | 3505                 | 1808        |
| 14754               | 13586             | 3449                   | 3542                 | 1624        |
| 14836               | 13280             | 3602                   | 3483                 | 1643        |
| 14690               | 13352             | 3508                   | 3502                 | 1787        |
| 14834               | 13382             | 3534                   | 3493                 | 1654        |
| 15168               | 13356             | 3480                   | 3687                 | 1714        |
| 15127               | 13142             | 3523                   | 3512                 | 1784        |
| 14451               | 13232             | 3583                   | 3541                 | 1644        |
| 14814               | 13132             | 3536                   | 3517                 | 1676        |
