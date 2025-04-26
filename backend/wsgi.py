from app import create_app

application = create_app()
app = application  # Garantir que ambos os nomes estejam disponíveis

if __name__ == "__main__":
    application.run(host="0.0.0.0", port=5000)