# Building efficient API

Today there exist many different technology stacks and frameworks to build web application server. Some are easier to get started than others. However, there are often hidden nuances about the tech stack that a developer must be aware of when it comes to writing code that can scale.

In this repo I am going to set up multiple mini projects for the purpose of comparing how different API code design can vastly affect performance.

Topics that I intend to cover:

- Django REST Framework
- Django Ninja
- Flask
- Fast API
- Golang

# Data model

For this experiment, we are going to set up a couple small data models the same way in each of the tech stacks:

```
+------------+              +------------+
|     Car    |              |  CarModel  |
+------------+              +------------+
|  model_id  | -----------> |     id     |
+------------+              +------------+
```

The Car and CarModel models each has a few more attributes themselves, but this demonstrates the 1-to-many relation between them.

## Django REST Framework (DRF)

Django is an out-of-box solution and the go-to choice for startups and hobby projects alike. It has one of the most feature rich ORM and migration systems today. Django REST Framework has been a defacto go-to for those who are using Django as a web application backend.

- build: `make docker-build`
- run: `make docker-up`
- populate database with 100k Car records: `make django-drf-populate`

#### Retrieving Car records Using DRF ModelSerializer

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

> TestResults
> First Byte: <span style="color:red">2565 ms</span>
> size: 15.11 MB

#### Retrieving Car records with related model attributes using DRF ModelSerializer

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

> TestResults
> First Byte: <span style="color:red">35226 ms</span>
> size: 21.36 MB

That took a whole lot longer.
The query in the API view `Car.objects.all()` did not contain data about each `Car` record's related `CarModel` record, by the time the Serializer is trying to serialize each record, Django has to fire off an additional query to fetch the related `CarModel` in order to get the `model_name`, `model_year` and `color` that the serializer is asking for. This is called N+1 query problem, and it's very common problem in stacks involving some sort of ORM.

In Django REST Framework, this can be a very easy mistake to make (simply by modifying a serializer), and luckily it's usually pretty simple to fix.

#### Optimizing retrieving Car records with related model attributes using query Prefetch

```python
# django_drf/car_registry/views.py
class CarListViewWithModelPrefetched(ListAPIView):
    serializer_class = CarSerializerWithRelatedModel
    queryset = Car.objects.all().prefetch_related('model')
```

Again, for comparison purpose, we keep the original API as-is, and added the modified API as a new API. Now we hit this new endpoint

> GET http://localhost:8000/retrieve-cars-with-prefetch-related/

> TestResults
> First Byte: <span style="color:red">2965 ms</span>
> size: 21.36 MB

Now we are back down to under 3 seconds.

The `prefetch_related('model')` tells to the ORM to perform a join with the `CarModel` model, and the returned data from databsae contains all of the attributes of `CarModel`, so when the serializer tries to access those attributes, the ORM does not need to query the database again. Thus the N+1 query problem is eliminated.

This is typically where most Django REST Framework application would stop at in terms of API query optimization. However, sometimes we are requesting so much data, this is still not enough. But first, let's re-organize our project structure a little bit.

#### Changing up the project structure a bit

We are going to leave the previous implemented serializers.py and views.py where they are for now even though we will not be using them anymore.

We want to set up a project that has 3 tiers, Models, Services, and APIs. In doing so we are going to keep our Service and API codes out side of Django app directory, but we are going to leave the Django app directories as the repositories for models. This allows us to develope complicated services that make use of multiple models across different Django apps if needed. In a nutshell:

```
/django_project_root
|-/project_level_config
|-/apis
  |-/some_api.py
  |-/some_other_api.py
|-/services
  |-/feature_a_services.py
  |-/feature_b_services.py
  |-...
|-/app_1
  |--/app_1_models.py
|-/app_2
  |--/app_2_models.py
|-...
```

I also do not like separating Serializer implementation from the API View implementation. As you have seen previously, it's very easy for a developer to make a little change for 1 serializer and somehow causes performance optimizing problems in serializers and views elsewhere. I would put the serializer and the view implementation together in a `some_api.py`.

You could probably also put all of the Django app modules in a repository directory. In a way we are opting to use Django mostly only as a Model Repository, and we want to manage rest of the Django project structure ourselves more or less in a different pattern. But we won't do that here.

With these in mind, we are going to implement the following:

```python
# django_drf/services/car_services.py
class CarService:
    def retrieve_all_cars(self):
        pass

# django_drf/apis/car_listing_api.py
class CarListingAPI(APIView):
    def get(self, request: Request, *args, **kwargs) -> Response:
        print(request)
        return Response({'detail': 'to be implemented'}, status=status.HTTP_501_NOT_IMPLEMENTED)
```

Now we are ready to flesh out some of the implementation details next.
