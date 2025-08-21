from app import create_app #importa la función create_app() que tú definiste en app/__init__.py.

app = create_app() # crea una instancia de tu aplicación Flask usando la configuración que ya definiste (como la base de datos, blueprints, etc.).

if __name__ == "__main__": # esta línea se asegura de que solo se ejecute app.run() si estás ejecutando directamente python run.py.
    app.run(host="0.0.0.0", debug=True)
