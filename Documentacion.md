  Iniciar entorno virtual, dentro del directorio de trabajo :

```bash
python3 -m venv venv
source venv/bin/activate
```

consulta POST por medio de curl:

```bash
curl -X POST http://localhost:5000/api/usuarios/login -H "Content-Type: application/json" -d '{"email": "michi123@gmail.com", "contrasena": "michi123"}'


curl -X GET http://localhost:5000/api/usuarios/ver_usuarios \
-H "Authorization: Bearer [token] ""
```

[Comprendiendo JWT y como implementar un JWT simple con Flask](https://4geeks.com/es/lesson/que-es-jwt-y-como-implementarlo-con-flask)

Como almacenar el token al hacer la solicitud 
