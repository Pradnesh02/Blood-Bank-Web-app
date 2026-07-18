from app import create_app

app = create_app()

if __name__ == '__main__':
    # Debug flag will follow config
    app.run()
