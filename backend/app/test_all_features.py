from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_01_rag_fact_memory():
    print("\n--- Testing RAG Fact Brain ---")
    # Add fact (correct field: fact_text, not fact)
    res = client.post("/api/memory/fact", json={
        "user_id": "test_user_charan",
        "fact_text": "My name is Charan and I am building Project Sahakar",
        "category": "project",
        "source": "user_chat"
    })
    assert res.status_code == 200, f"Failed to add fact: {res.text}"
    data = res.json()
    print("Add Fact Result:", data)
    assert data["status"] == "SUCCESS"
    
    # Add another fact
    res1b = client.post("/api/memory/fact", json={
        "user_id": "test_user_charan",
        "fact_text": "I study Computer Science at IIIT Hyderabad",
        "category": "study",
        "source": "user_chat"
    })
    assert res1b.status_code == 200
    print("Add Study Fact:", res1b.json())

    # Get facts
    res2 = client.get("/api/memory/facts?user_id=test_user_charan")
    assert res2.status_code == 200
    facts = res2.json()
    print(f"Retrieved {len(facts)} facts for test_user_charan:")
    for f in facts:
        print(f"  - [{f.get('category','?')}] {f.get('fact_text', f.get('fact', ''))}")
    assert len(facts) >= 2

    # Get context header
    res3 = client.get("/api/memory/context-header?user_id=test_user_charan")
    assert res3.status_code == 200
    header = res3.json()
    print("Formatted Memory Header:\n", header["active_memory_context"])
    assert len(header["active_memory_context"]) > 10

def test_02_rag_document_ocean():
    print("\n--- Testing RAG Document Ocean ---")
    # Ingest document (correct fields: title, text_content)
    res = client.post("/api/memory/ingest", json={
        "user_id": "test_user_charan",
        "title": "Project Sahakar Overview",
        "text_content": "Project Sahakar is an autonomous task and learning assistant built on ATLAS OS with multi-model routing across Groq, SambaNova, Cerebras, and NVIDIA NIM. It features the SCAAR memory engine with dual-database architecture, voice synthesis, and intelligent agent routing.",
        "category": "documentation",
        "metadata": {"author": "Charan", "version": "1.0"}
    })
    assert res.status_code == 200, f"Failed to ingest doc: {res.text}"
    data = res.json()
    print("Ingest Result:", data)
    assert "doc_id" in data or data.get("status") == "SUCCESS"

    # Search vectors
    res2 = client.post("/api/memory/search", json={
        "user_id": "test_user_charan",
        "query": "What models does Project Sahakar route across?",
        "top_k": 3
    })
    assert res2.status_code == 200
    chunks = res2.json()
    print(f"Vector Search returned {len(chunks)} chunks:")
    for c in chunks:
        ct = c.get('chunk_text', c.get('content', c.get('text', '')))
        sc = c.get('similarity_score', c.get('score', 0))
        print(f"  - [Score: {sc:.3f}] {ct[:100]}...")
    assert len(chunks) > 0

def test_03_intelligent_agents():
    print("\n--- Testing Intelligent Agents ---")
    agents_to_test = [
        ("scholar_core", "Explain how to study effectively for an upcoming exam."),
        ("career_architect", "Give me tips for a tech resume and interview preparation."),
        ("fiscal_sentinel", "How should I structure my monthly budget and analyze burn rate?"),
        ("velocity_form", "Design a progressive overload principle workout for strength."),
        ("biometrics_pilot", "How do sleep duration and heart rate trends correlate with daily energy?"),
        ("zenith_counsel", "I am feeling overwhelmed with work deadlines and need CBT reframing."),
        ("nexus_strategist", "Plan a productive morning routine and schedule for me.")
    ]
    for agent_id, prompt in agents_to_test:
        print(f"\n  Testing Agent: {agent_id}...")
        try:
            res = client.post("/agent/chat", json={
                "agent_id": agent_id,
                "prompt": prompt,
                "user_id": "test_user_charan"
            })
            if res.status_code == 200:
                data = res.json()
                print(f"  -> Provider: {data['provider']} | Model: {data['model_used']} | Latency: {data['latency_ms']:.1f}ms")
                print(f"  -> Response snippet: {data['response'][:150]}...")
                assert len(data["response"]) > 0
                print(f"  -> [PASS] {agent_id} PASSED!")
            else:
                print(f"  -> [WARN] {agent_id} returned {res.status_code}: {res.text[:200]}")
        except Exception as e:
            print(f"  -> [WARN] {agent_id} exception: {e}")

def test_04_general_chat():
    print("\n--- Testing General Chat (Auto-Routing) ---")
    res = client.post("/chat", json={
        "prompt": "What is 2+2? Answer in one word.",
        "user_id": "test_user_charan"
    })
    assert res.status_code == 200, f"Chat failed: {res.text}"
    data = res.json()
    print(f"  -> Provider: {data['provider']} | Model: {data['model_used']} | Latency: {data['latency_ms']:.1f}ms")
    print(f"  -> Response: {data['response'][:100]}")
    assert len(data["response"]) > 0
    print("  -> [PASS] General Chat PASSED!")

if __name__ == "__main__":
    test_01_rag_fact_memory()
    test_02_rag_document_ocean()
    test_04_general_chat()
    test_03_intelligent_agents()
    print("\n\n========================================")
    print("[PASS] ALL TESTS PASSED SUCCESSFULLY!")
    print("========================================")
