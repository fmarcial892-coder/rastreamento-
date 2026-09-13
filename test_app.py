from app import app

with app.test_client() as client:
    for path in ["/", "/privacidade", "/termos"]:
        response = client.get(path)
        assert response.status_code == 200, (path, response.status_code)
    html = client.get("/").get_data(as_text=True)
    for marker in ["Rastreamento de Entrega", "CEP", "Código de Rastreio", "AMBIENTE INTERNO"]:
        assert marker in html, marker
    assert 'id="cpf"' not in html
    assert 'id="tracking-code"' in html
print("routes=OK no-cpf=OK address-fields=OK")
