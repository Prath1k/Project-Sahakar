import json
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

print('\n--- Testing Feature: NexusStrategist request ---')
response = client.post('/agent/chat', json={
    'agent_id': 'nexus_strategist',
    'prompt': 'Plan a 3-day tech tour in San Francisco on a $500 budget.'
})
print('Status Code:', response.status_code)
if response.status_code == 200:
    data = response.json()
    print('Model Used:', data.get('model_used'))
    print('Provider:', data.get('provider').split(' (')[0])
    print('Response Snippet:', data.get('response')[:250].replace('\n', ' '))
    print('Is Safe:', data.get('is_safe'))
else:
    print('Error:', response.text)
