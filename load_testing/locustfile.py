
import threading
from locust import HttpUser, task, between

# Create a global lock object
task_lock = threading.Lock()

class ApiLoadTest(HttpUser):
    wait_time = between(1, 3)  # Time between tasks (1 to 3 seconds)
    host = "http://localhost"
    @task(1)
    def test_drf_with_serializer(self):
        with task_lock:  # Only one task can run at a time due to this lock
            response = self.client.get("http://localhost:8000/drf/with-serializer/")
            print(f"DRF with serializer response time: {response.elapsed.total_seconds()} seconds")

    @task(1)
    def test_drf_without_serializer(self):
        with task_lock:
            response = self.client.get("http://localhost:8000/drf/without-serializer/")
            print(f"DRF without serializer response time: {response.elapsed.total_seconds()} seconds")

    @task(1)
    def test_ninja_with_schema(self):
        with task_lock:
            response = self.client.get("http://localhost:8001/ninja/with-schema/")
            print(f"Django ninja with schema response time: {response.elapsed.total_seconds()} seconds")

    @task(1)
    def test_ninja_without_schema(self):
        # with task_lock:
        response = self.client.get("http://localhost:8001/ninja/without-schema/")
        print(f"Django ninja without schema response time: {response.elapsed.total_seconds()} seconds")

    @task(1)
    def test_fastapi_with_pydantic(self):
        with task_lock:
            response = self.client.get("http://localhost:8002/fastapi/")
            print(f"FastAPI response time: {response.elapsed.total_seconds()} seconds")

    @task(1)
    def test_go(self):
        with task_lock:
            response = self.client.get("http://localhost:8003/go/")
            print(f"Go response time: {response.elapsed.total_seconds()} seconds")