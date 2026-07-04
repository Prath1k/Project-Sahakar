import json
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

print('\n--- Testing Feature: ZenithCounsel request ---')
response = client.post('/agent/chat', json={
    'agent_id': 'zenith_counsel',
    'prompt': 'I am completely failing this class and my life is over. I can not do anything right.'
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
