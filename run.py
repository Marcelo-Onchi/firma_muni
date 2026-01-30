# run.py
print(">>> run.py ejecutándose...")

from app import create_app

app = create_app()

print(">>> app creada OK. Iniciando servidor...")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5010, debug=True)
