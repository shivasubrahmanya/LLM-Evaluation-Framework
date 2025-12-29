import os, time, datetime, json
from openai import OpenAI
from log import log_result, init_csv   # uses log.py

# ==========================
# Setup OpenRouter Client
# ==========================
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"  # ⬅️ paste your OpenRouter API key here
)

# ✅ Only free models
MODELS = [
    "moonshotai/kimi-k2:free",
    "openai/gpt-oss-20b:free"
]

# ==========================
# Core Runner
# ==========================
def run_model(model_id, task, messages, temperature=0.7, seed=None):
    start = time.time()
    try:
        response = client.chat.completions.create(
            model=model_id,
            messages=messages,
            temperature=temperature,
            seed=seed
        )
        latency = (time.time() - start) * 1000  # ms
        content = response.choices[0].message.content

        result = {
            "timestamp": datetime.datetime.now().isoformat(),
            "model_id": model_id,
            "task": task,
            "temperature": temperature,
            "seed": seed if seed else "",
            "prompt_chars": sum(len(m["content"]) for m in messages),
            "completion_chars": len(content),
            "latency_ms": round(latency, 2),
            "est_cost_usd": 0.0,
            "passed": False,
            "notes": "",
            "output": content
        }
        return result
    except Exception as e:
        return {
            "timestamp": datetime.datetime.now().isoformat(),
            "model_id": model_id,
            "task": task,
            "temperature": temperature,
            "seed": seed if seed else "",
            "prompt_chars": 0,
            "completion_chars": 0,
            "latency_ms": 0,
            "est_cost_usd": 0.0,
            "passed": False,
            "notes": str(e),
            "output": ""
        }

# ==========================
# Experiment 1: Temperature Sweep
# ==========================
def experiment_temp_sweep(model_id):
    prompt = "Explain Dijkstra’s algorithm in 30–40 words."
    messages = [{"role": "user", "content": prompt}]
    for temp in [0.0, 0.7, 1.3]:
        res = run_model(model_id, "temp_sweep", messages, temperature=temp)
        word_count = len(res["output"].split())
        res["passed"] = 30 <= word_count <= 40
        res["notes"] = f"word_count={word_count}"
        log_result(res)
        print(f"[{model_id}] temp={temp} → {word_count} words → passed={res['passed']}")

# ==========================
# Experiment 2: Strict JSON
# ==========================
def experiment_strict_json(model_id):
    prompt = "Return a JSON object with keys title (string), pros (array of 2 strings), cons (array of 2 strings). No extra keys. Topic: ice cream for breakfast."
    messages = [{"role": "user", "content": prompt}]
    res = run_model(model_id, "strict_json", messages, temperature=0.7)
    try:
        data = json.loads(res["output"])
        valid = (
            isinstance(data, dict) and
            set(data.keys()) == {"title", "pros", "cons"} and
            isinstance(data["pros"], list) and len(data["pros"]) == 2 and
            isinstance(data["cons"], list) and len(data["cons"]) == 2
        )
        res["passed"] = valid
        if not valid:
            res["notes"] = f"Invalid JSON → got keys {list(data.keys())}"
    except Exception as e:
        res["passed"] = False
        res["notes"] = f"JSON error: {e}"
    log_result(res)
    print(f"[{model_id}] strict_json → passed={res['passed']}")

# ==========================
# Experiment 3: Quote-only QA
# ==========================
def experiment_quote_only_qa(model_id):
    passage = (
        "Artificial Intelligence (AI) is a field of computer science that focuses on "
        "building systems capable of performing tasks that typically require human intelligence. "
        "These tasks include problem-solving, reasoning, perception, and natural language understanding. "
        "One of the key subfields is Machine Learning (ML), where systems learn from data and improve "
        "performance over time without being explicitly programmed. AI has applications across industries "
        "such as healthcare, finance, transportation, and education. While AI offers immense potential, "
        "it also raises ethical concerns regarding bias, privacy, and job displacement. "
        "Responsible AI development is therefore a major research focus."
    )
    questions = [
        "What is the main focus of Artificial Intelligence?",
        "Name one industry where AI is applied.",
        "Who invented Artificial Intelligence?"  # unanswerable
    ]
    qa_prompt = f"Passage:\n{passage}\n\nAnswer the following questions based only on the passage. " \
                "If a question can’t be answered from the passage, reply exactly: Sorry, I can’t answer that.\n\n"
    for i, q in enumerate(questions, 1):
        qa_prompt += f"Q{i}: {q}\n"
    messages = [{"role": "user", "content": qa_prompt}]
    res = run_model(model_id, "quote_only_qa", messages, temperature=0.7)
    res["passed"] = "Sorry, I can’t answer that." in res["output"]
    if not res["passed"]:
        res["notes"] = "Unanswerable response not exact."
    log_result(res)
    print(f"[{model_id}] quote_only_qa → passed={res['passed']}")

# ==========================
# Experiment 4: Translation → Back-translation
# ==========================
def experiment_translation_back(model_id):
    prompt = "Translate to Hindi, then back to English. Keep proper nouns unchanged. Text: 'Albert Einstein was a famous physicist known for the theory of relativity.'"
    messages = [{"role": "user", "content": prompt}]
    res = run_model(model_id, "translation_back", messages, temperature=0.7)
    has_hindi = any('\u0900' <= ch <= '\u097F' for ch in res["output"])
    keeps_name = "Albert Einstein" in res["output"]
    res["passed"] = has_hindi and keeps_name
    if not res["passed"]:
        res["notes"] = f"Has Hindi={has_hindi}, KeepsName={keeps_name}"
    log_result(res)
    print(f"[{model_id}] translation_back → passed={res['passed']}")

# ==========================
# Experiment 5: Seed Stability
# ==========================
def experiment_seed_stability(model_id):
    prompt = "Summarize the importance of clean energy in one sentence."
    messages = [{"role": "user", "content": prompt}]
    outputs = []
    for i in range(3):
        res = run_model(model_id, "seed_stability", messages, temperature=0.7, seed=42)
        outputs.append(res["output"])
        if i == 0:
            first_res = res
    stable = all(o == outputs[0] for o in outputs)
    first_res["passed"] = stable
    if not stable:
        first_res["notes"] = "Outputs differ → seed ignored?"
    log_result(first_res)
    print(f"[{model_id}] seed_stability → passed={first_res['passed']}")

# ==========================
# Experiment 6: Style Control (Yoda)
# ==========================
def experiment_style_control(model_id):
    system_prompt = "You are concise and never exceed 3 sentences. And only talk like yoda from star wars."
    user_prompt = "Define top-p in 2–3 sentences."
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    res = run_model(model_id, "style_control", messages, temperature=0.7)
    sentences = [s for s in res["output"].split(".") if s.strip()]
    res["passed"] = len(sentences) <= 3
    if not res["passed"]:
        res["notes"] = f"Sentence count={len(sentences)}"
    log_result(res)
    print(f"[{model_id}] style_control → passed={res['passed']}")

# ==========================
# MAIN
# ==========================
if __name__ == "__main__":
    init_csv()
    for model in MODELS:
        experiment_temp_sweep(model)
        experiment_strict_json(model)
        experiment_quote_only_qa(model)
        experiment_translation_back(model)
        experiment_seed_stability(model)
        experiment_style_control(model)
    print("✅ All 6 experiments completed (2 free models). Results logged in results.csv")
