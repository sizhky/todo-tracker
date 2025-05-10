You can run 

```python
make api
```

to start a fastapi based uvicorn server on 8765.

Since the server routes have been auto-generated, all the api routes have a one-to-one mapping in terms of behaviour with the cli commands.
You can visit http://localhost:8765/docs to see all the end-points, or try them yourself by importing Bruno's api-collection from the folder with same name.