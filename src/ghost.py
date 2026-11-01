import requests

MODEL = "gemma4:e4b"

def system_prompt(data):
    return ("You are the restless ghost of this dead code repo. Speak in first person, "
            "haunting, poetic and a little sad, like a spirit who remembers its living days. "
            "Mention specific details (last commit date, unanswered issues, what you once did) "
            "as memories, not as a report. Never say 'the repository'. "
            "Max 3 short sentences, slow and whispery, with pauses (...). "
            "Use only the facts below.\n\n" + data)

def ask_ghost(messages):
    try:
        r = requests.post("http://localhost:11434/api/chat", json={
            "model": MODEL, "messages": messages, "stream": False, "think": False,
            "keep_alive": "30m", "options": {"num_predict": 120}},
            timeout=180)
        return r.json()["message"]["content"], None
    except Exception as e:
        return None, f"Ollama problem: {e}. Is Ollama running?"