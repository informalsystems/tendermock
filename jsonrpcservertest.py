from jsonrpcserver import Success, method, serve, Result

@method
def hello(name: str) -> Result:
    return Success("Hello " + name)

if __name__ == "__main__":
    serve()