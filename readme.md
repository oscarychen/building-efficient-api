# Building efficient REST APIs with Django

Today there are many technology stacks and frameworks to build web applications. Some are easier to start with than others. However, there are often hidden nuances about the tech stack that developers must be aware of when writing scalable code.

In this repo, I will set up multiple mini projects to compare how different API code designs can affect performance.

Topics to cover:

- Django REST Framework
- Django Ninja
- Golang

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
- run: `make docker-up`
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

> Response code: 200 (OK); Time: 2432ms (2 s 432 ms); Content length: 15107465 bytes (15.11 MB)

### Chapter 2: Retrieving Car records with related model attributes using DRF ModelSerializer

Next, we are going to want to return some additional data for each of the Car record retrieved while maintaining the response data structure, particular the related CarModel's attributes `name`, `year`, and `color`. Most Django developers would do the following changes to the serializer:

```python
# django_drf/car_registry/serializers.py
class CarSerializerWithRelatedModel(serializers.ModelSerializer):
    model_name = serializers.CharField(source='model.name', read_only=True)
    model_year = serializers.IntegerField(source='model.year', read_only=True)
    color = serializers.CharField(source='model.color', read_only=True)
    class Meta:
        model = Car
        fields = '__all__'
```

For comparison purpose, we keep the original API as-is, and added the modified API as a new API. Now we hit this new endpoint

> GET http://localhost:8000/retrieve-cars-with-model/

> Response code: 200 (OK); Time: 30801ms (30 s 801 ms); Content length: 21356443 bytes (21.36 MB)

That took a lot longer.
The query in the API view `Car.objects.all()` did not contain data about each `Car` record's related `CarModel` record, by the time the Serializer is trying to serialize each record, Django has to fire off an additional query to fetch the related `CarModel` in order to get the `model_name`, `model_year` and `color` that the serializer is asking for. This is called N+1 query problem, and it's very common problem in stacks involving some sort of ORM.

In Django REST Framework, this can be a very easy mistake to make (simply by modifying a serializer) and sometimes not easy to spot; luckily it's usually pretty simple to fix.

### Chapter 3: Optimizing retrieving Car records with related model attributes using query Prefetch

Based on the previous example, we are going to modify the query by "prefetching" the related records:

```python
# django_drf/car_registry/views.py
class CarListViewWithModelPrefetched(ListAPIView):
    serializer_class = CarSerializerWithRelatedModel
    queryset = Car.objects.all().prefetch_related('model')
```

Again, for comparison purpose, we keep the previous API as-is, and added the modified API as a new API. Now we hit this new endpoint

> GET http://localhost:8000/retrieve-cars-with-prefetch-related/

> Response code: 200 (OK); Time: 3199ms (3 s 199 ms); Content length: 21356443 bytes (21.36 MB)

Now we are back down to around 3 seconds.

The `prefetch_related('model')` tells to the ORM to perform a join with the `CarModel` model, and the returned data from database contains all the attributes of `CarModel`, so when the serializer tries to access those attributes, the ORM does not need to query the database again, thus the N+1 query problem is eliminated.

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

I also do not like separating Serializer implementation from the API View implementation. Saving a bit of code duplication but create coupling between serializers and therefore APIs can be a source of problem in larger teams. As you have seen previously, it's very easy for a developer to make a little change in 1 serializer and somehow causes performance optimizing problems in serializers and views elsewhere. I would put the serializer and the view implementation together in a `some_api.py`, in fact I would put request param serializer, request body data serializer, and response serializer implementation all in the same file with the API View implementation that they are responsible for.

You could probably also put all the Django app modules in a repository directory. In a way we are opting to use Django mostly only as a Model Repository, and we want to manage rest of the Django project structure ourselves more or less in a different pattern. But we won't go that far.

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
        return Car.objects.all().prefetch_related('model')
    
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

> Response code: 200 (OK); Time: 2867ms (2 s 867 ms); Content length: 20267548 bytes (20.27 MB)

This is a little bit faster than previous implementation, but not by much. The DRF Serializer is still iterating through each of the Car instances to turn it into a Python dictionary. There are few other things you can try here in Python to speed up the process, but we are going to move onto something else.

### Chapter 6: Using Django ORM more and DRF Serializer less
Next we are going to write the query in a way that we can get the data we want directly from the database, so that we can skip turning the data into Python dictionaries before serializing them into json.

Building on the existing CarService class:
```python
# django_drf/services/car_services.py
class CarService:
    def retrieve_all_cars(self):
        return Car.objects.all().prefetch_related('model')

    def retrieve_all_cars_annotated(self):
        qs = self.retrieve_all_cars()
        qs = qs.annotate(
            model_name=F('model__name'),
            model_year=F('model__year'),
            color=F('model__color')
        )
        return qs

    def retrieve_all_cars_as_dicts(self):
        cars = self.retrieve_all_cars_annotated()
        return cars.values(
            'vin',
            'owner',
            'created_at',
            'updated_at',
            'model_id',
            'model_name',
            'model_year',
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

> Response code: 200 (OK); Time: 1241ms (1 s 241 ms); Content length: 20567548 bytes (20.57 MB)

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

> Response code: 200 (OK); Time: 908ms (908 ms); Content length: 21567548 bytes (21.57 MB)

And now we are able to get this API to return in under 1 second with 100k records with data across 2 tables.

### Chapter 8: Other performance considerations
At this point we have optimized the API from database query to response serialization. There are still some other areas that would affect API performance:
- database indexing: It is likely that you would have some sort of filtering in the query, which means you need to consider database indexing
- query caching: especially if the data is relatively static
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

> Response code: 200 (OK); Time: 61ms (61 ms); Content length: 216164 bytes (216.16 kB)

As expected, the response is much smaller and faster to return.