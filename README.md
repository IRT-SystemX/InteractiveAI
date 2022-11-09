# CAB Assistant Platform

# Build and run event service
```
docker build -t event-service .
```

```
docker run -p 5000:5000 event-service
```

# Docs
A postman collection is under docs/postman_collections, and you can always check the openapi through the URL http://localhost:5000/docs