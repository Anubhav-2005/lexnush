from lexnush import create_app

# Gunicorn imports this object after Render has injected the production
# environment. create_app() therefore validates DATABASE_URL before serving.
app = create_app()

if __name__ == "__main__":
    app.run()
