# txn-anomaly-api

A small Python service that tells whether a transaction amount looks unusual.
I wrote it for the course Applied Software Development Project (Assignment 5)
as a sample research project for practicing Docker and a Jenkins CI pipeline.
The topic is close to my master's thesis about real-time monitoring of financial
transactions.

## What it does

The service learns what a normal amount looks like from a baseline of fake
transactions (generated with a fixed seed, so every run gives the same
baseline). For every new amount it computes a z-score on the logarithm of the
amount. If the amount is more than 3 standard deviations away from normal, in
either direction, it is marked as suspicious.

| Method and path | Description |
|-----------------|-------------|
| GET /health | Returns status and version |
| GET /baseline | Shows the learned baseline |
| POST /score | Body `{"amount": 123.45}`, returns z-score and `suspicious` flag |

This is a simple statistical rule made for learning. It is not a real fraud
detection model.

## Project structure

```
app/            application code (data, scoring, FastAPI app)
tests/          25 pytest tests
Dockerfile      multi stage: base, test, runtime
Jenkinsfile     CI pipeline
jenkins/        Dockerfile and compose file for a local Jenkins
requirements.txt, requirements-dev.txt   pinned dependencies
```

## Run locally without Docker

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
pytest
uvicorn app.main:app --reload
```

Open http://localhost:8000/docs to try the API in the browser.

## Run with Docker

```bash
docker build -t txn-anomaly-api .
docker run --rm -p 8000:8000 txn-anomaly-api
curl -X POST http://localhost:8000/score -H "Content-Type: application/json" -d '{"amount": 5000000}'
```

Run the tests inside Docker (the same way Jenkins does):

```bash
docker build --target test -t txn-anomaly-api:test .
docker run --rm txn-anomaly-api:test
```

## Jenkins pipeline

The `Jenkinsfile` has these stages:

1. **Checkout** gets the code from Git.
2. **Unit tests** builds the `test` image and runs pytest inside it, then
   publishes the JUnit result in Jenkins.
3. **Build image** builds the final small image and tags it with the build number.
4. **Smoke test** starts the container and checks that `/health` answers.
5. **Push to Docker Hub** runs only when the parameter `PUSH_IMAGE` is on. It
   needs a Jenkins credential with the id `dockerhub-creds`.

Jenkins checks the repository for new commits every 2 minutes (`pollSCM`), so
every commit starts a new build.

### Start a local Jenkins

```bash
docker compose -f jenkins/docker-compose.yml up -d --build
docker compose -f jenkins/docker-compose.yml exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

Open http://localhost:8080, enter the password, create an admin user, then
create a Pipeline job with "Pipeline script from SCM", this repository URL,
branch `*/main` and script path `Jenkinsfile`.

Warning: this Jenkins runs as root and controls the Docker engine of your
computer. Use it only locally for learning.

## Reproducibility notes

- Dependency versions are pinned in the requirements files.
- The Python version is fixed by the base image `python:3.12-slim`.
- The baseline data uses a fixed random seed.
- Tests run in the same container environment as the final image.

## License

MIT, see [LICENSE](LICENSE).
