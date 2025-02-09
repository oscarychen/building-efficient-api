
import threading
from locust import HttpUser, task, between, FastHttpUser, tag

# Create a global lock object
task_lock = threading.Lock()

class ApiLoadTest(FastHttpUser):
    wait_time = between(1, 3)  # Time between tasks (1 to 3 seconds)
    host = "http://localhost"

    @tag("drf_with_serializer")
    @task(1)
    def test_drf_with_serializer(self):
        with task_lock:  # Only one task can run at a time due to this lock
            self.client.get("http://django-drf:8000/drf/with-serializer/")

    @tag("drf_without_serializer")
    @task(1)
    def test_drf_without_serializer(self):
        with task_lock:
            self.client.get("http://django-drf:8000/drf/without-serializer/")

    @tag("ninja_with_schema")
    @task(1)
    def test_ninja_with_schema(self):
        with task_lock:
            self.client.get("http://django-ninja:8001/ninja/with-schema/")

    @tag("ninja_without_schema")
    @task(1)
    def test_ninja_without_schema(self):
        with task_lock:
            self.client.get("http://django-ninja:8001/ninja/without-schema/")

    @tag("fastapi_with_pydantic")
    @task(1)
    def test_fastapi_with_pydantic(self):
        with task_lock:
            self.client.get("http://fastapi:8002/fastapi/")

    @tag("go")
    @task(1)
    def test_go(self):
        with task_lock:
            self.client.get("http://go-sqlc-mux:8003/go/")