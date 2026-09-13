from app import app

with app.test_client() as client:
    for path in ["/", "/privacidade", "/termos"]:
        response = client.get(path)
        assert response.status_code == 200, (path, response.status_code)
    html = client.get("/").get_data(as_text=True)
    for marker in ["DEMONSTRAÇÃO EDUCATIVA", "NÃO É UM RASTREAMENTO OFICIAL", "CPF de teste", "Simulação local"]:
        assert marker in html, marker
    assert "ViaCEP" in open("templates/privacy.html", encoding="utf-8").read()
print("routes=OK demo-disclosure=OK")
