# IsoQuaC

## Installation

- Install Docker
- Run the following command:

```bash
docker compose build
```

- Install the job itself:

```bash
docker build -t isoquac-job:v1.0.0
```

Where v1.0.0 is the latest version.
TODO: Change the isoquac-job install logic to accomodate versioning.

- Running it:

```bash
docker compose up -d
```

- Now you should be able to go to http://localhost:8080
