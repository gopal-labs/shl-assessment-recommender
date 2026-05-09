import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch, MagicMock
from app.models.schemas import ChatResponse, Recommendation

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

# Mocking the agent so we don't call actual LLM during basic schema/routing tests
@patch('app.routes.chat.run_agent')
def test_chat_endpoint_schema(mock_run_agent):
    mock_run_agent.return_value = ChatResponse(
        reply="Clarification question.",
        recommendations=[],
        end_of_conversation=False
    )
    
    response = client.post("/chat", json={
        "messages": [
            {"role": "user", "content": "I need an assessment"}
        ]
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert "recommendations" in data
    assert "end_of_conversation" in data
    assert data["recommendations"] == []
    assert data["end_of_conversation"] is False

@patch('app.routes.chat.run_agent')
def test_chat_endpoint_recommendation(mock_run_agent):
    mock_run_agent.return_value = ChatResponse(
        reply="Here are some options.",
        recommendations=[
            Recommendation(name="Test 1", url="http://test.com", test_type="K")
        ],
        end_of_conversation=False
    )
    
    response = client.post("/chat", json={
        "messages": [
            {"role": "user", "content": "I need a Java test"}
        ]
    })
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["recommendations"]) == 1
    assert data["recommendations"][0]["name"] == "Test 1"

@patch('app.routes.chat.run_agent')
def test_chat_endpoint_end_conversation(mock_run_agent):
    mock_run_agent.return_value = ChatResponse(
        reply="Glad I could help.",
        recommendations=[],
        end_of_conversation=True
    )
    
    response = client.post("/chat", json={
        "messages": [
            {"role": "user", "content": "Perfect, thanks."}
        ]
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["end_of_conversation"] is True
