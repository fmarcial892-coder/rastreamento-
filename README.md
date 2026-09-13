# Rastreia Fácil — demonstração educativa

Protótipo de interface de rastreamento, sem marca real e sem integração com transportadora. O fluxo usa dados fictícios, consulta o CEP público pelo ViaCEP e calcula a barra de progresso apenas no navegador.

## Rodar localmente

```bash
pip install -r requirements.txt
python app.py
```

O formulário não envia nem persiste CPF ou endereço no backend. A barra, os status e o prazo de uma hora são exclusivamente demonstrativos e reiniciam ao recarregar a página.

## Escopo

O projeto não deve ser apresentado como rastreamento oficial, nem ser usado para coletar dados pessoais reais. Para um produto real, seria necessária autorização da marca, integração oficial de pedidos/entregas, base legal LGPD, controle de acesso e política de retenção de dados.
