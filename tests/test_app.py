"""
Unit and integration tests for the Flask Password Assistant application.
"""
import sys
import os
import json
import pytest

# Add password-ml-app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'password-ml-app'))

from app import app


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_health_endpoint(client):
    """Test that the /health endpoint returns 200 OK."""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert data['service'] == 'password-assistant'


def test_api_analyze_endpoint_weak_password(client):
    """Test /api/analyze endpoint with a weak password."""
    response = client.post('/api/analyze',
                          data=json.dumps({'password': 'weak'}),
                          content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # Verify response structure
    assert 'input_password' in data
    assert 'predicted_strength' in data
    assert 'issues_found' in data
    assert 'suggestions' in data
    assert 'estimated_crack_time' in data
    
    # Verify data types
    assert isinstance(data['input_password'], str)
    assert isinstance(data['predicted_strength'], str)
    assert isinstance(data['issues_found'], list)
    assert isinstance(data['suggestions'], list)
    assert isinstance(data['estimated_crack_time'], str)
    
    # Weak password should have issues
    assert len(data['issues_found']) > 0


def test_api_analyze_endpoint_strong_password(client):
    """Test /api/analyze endpoint with a strong password."""
    response = client.post('/api/analyze',
                          data=json.dumps({'password': 'MyStr0ng!P@ssw0rd2024'}),
                          content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # Verify response structure
    assert 'input_password' in data
    assert 'predicted_strength' in data
    assert data['predicted_strength'] in ['Weak', 'Medium', 'Strong']
    
    # Strong password should have fewer or no issues
    assert isinstance(data['issues_found'], list)


def test_api_analyze_endpoint_empty_password(client):
    """Test /api/analyze endpoint with empty password."""
    response = client.post('/api/analyze',
                          data=json.dumps({'password': ''}),
                          content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'predicted_strength' in data


def test_api_analyze_endpoint_missing_password(client):
    """Test /api/analyze endpoint with missing password field."""
    response = client.post('/api/analyze',
                          data=json.dumps({}),
                          content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data)
    # Should handle missing password gracefully
    assert 'predicted_strength' in data


def test_index_endpoint_get(client):
    """Test that the index page loads correctly."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'html' in response.data or b'HTML' in response.data


def test_index_endpoint_post(client):
    """Test form submission on index page."""
    response = client.post('/', data={'password': 'TestPassword123!'})
    assert response.status_code == 200


def test_result_page_endpoint(client):
    """Test the result page endpoint."""
    response = client.post('/result', data={'password': 'TestPassword123!'})
    assert response.status_code == 200


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
