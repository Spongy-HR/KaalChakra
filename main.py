import requests
import time
import json
import re

# ============================================
# CONFIG
# ============================================
HOST = "192.168.239.1"
BASE_URL = f"http://{HOST}:8888/api/v2"

HEADERS = {
    "KEY": "ADMIN123",
    "Content-Type": "application/json"
}

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

AGENT_ID = None
ADVERSARIES = {}

LAST_ATTACK_TIME = 0
ATTACK_COOLDOWN = 60
LAST_ADVERSARY = None

# ============================================
# UI (UNCHANGED)
# ============================================

def banner():
    print("""
============================================================
                    VAPT AUTOMATION
============================================================
        AI-Driven Red Team Simulation Engine
------------------------------------------------------------
""")

def section(title):
    print("\n" + "-" * 55)
    print(f"[ {title} ]")
    print("-" * 55)

def log(msg): print(f"[+] {msg}")
def warn(msg): print(f"[!] {msg}")
def error(msg): print(f"[-] {msg}")

# ============================================
# HELPER
# ============================================

def normalize_response(res):
    return res if isinstance(res, list) else res.get("data", [])

# 🔥 NEW: confidence normalizer
def normalize_confidence(conf):
    try:
        # number case
        if isinstance(conf, (int, float)):
            if conf >= 0.75:
                return "high"
            elif conf >= 0.4:
                return "medium"
            else:
                return "low"

        # string case
        if isinstance(conf, str):
            c = conf.strip().lower()

            if c in ["high", "medium", "low"]:
                return c

            # numeric string
            try:
                val = float(c)
                return normalize_confidence(val)
            except:
                return "low"

    except:
        pass

    return "low"

# ============================================
# AGENT
# ============================================

def get_agents():
    global AGENT_ID

    try:
        r = requests.get(f"{BASE_URL}/agents", headers=HEADERS, timeout=10)
        data = normalize_response(r.json())

        alive = [a for a in data if a.get("status") == "alive"]

        if not alive:
            warn("No alive agent")
            return False

        AGENT_ID = alive[0].get("paw")
        log(f"Active Agent: {AGENT_ID}")
        return True

    except Exception as e:
        error(f"Agent error: {e}")
        return False

# ============================================
# ADVERSARIES
# ============================================

def load_adversaries():
    global ADVERSARIES

    section("Loading Adversaries")

    try:
        r = requests.get(f"{BASE_URL}/adversaries", headers=HEADERS, timeout=10)
        data = normalize_response(r.json())

        for adv in data:
            name = adv.get("name")
            adv_id = adv.get("adversary_id")

            if name and adv_id:
                ADVERSARIES[name.strip()] = adv_id

        log(f"Loaded: {len(ADVERSARIES)} adversaries")

    except Exception as e:
        error(f"Adversary error: {e}")

# ============================================
# ATTACK
# ============================================

def launch_attack(adversary_name):
    global LAST_ATTACK_TIME

    adversary_name = adversary_name.strip()

    if adversary_name not in ADVERSARIES:
        warn(f"Invalid adversary: {adversary_name}")
        return

    payload = {
        "name": f"AI Attack - {adversary_name}",
        "agents": [AGENT_ID],
        "adversary_id": ADVERSARIES[adversary_name]
    }

    section("Attack Execution")

    log(f"Adversary: {adversary_name}")
    log(f"ID: {ADVERSARIES[adversary_name]}")
    log(f"Target Agent: {AGENT_ID}")

    try:
        r = requests.post(f"{BASE_URL}/operations",
                          headers=HEADERS,
                          json=payload,
                          timeout=10)

        if r.status_code == 200:
            log("Attack launched")
            LAST_ATTACK_TIME = time.time()
        else:
            error(r.text[:200])

    except Exception as e:
        error(f"Launch error: {e}")

# ============================================
# LOGS
# ============================================

def extract_execution_data():
    try:
        r = requests.get(f"{BASE_URL}/operations", headers=HEADERS, timeout=10)
        data = normalize_response(r.json())

        if not data:
            return []

        latest = data[-1]

        execution = []

        for link in latest.get("chain", []):
            execution.append({
                "ability": link.get("ability", {}).get("name"),
                "technique": link.get("ability", {}).get("technique_name"),
                "status": link.get("status"),
                "output": link.get("output")
            })

        return execution

    except Exception as e:
        error(f"Log error: {e}")
        return []

# ============================================
# AI
# ============================================

def ask_ai(data):
    adversary_list = list(ADVERSARIES.keys())

    prompt = f"""
Analyze logs and choose best adversary.

Logs:
{json.dumps(data)}

Adversaries:
{adversary_list}

Return ONLY JSON:
{{"analysis":"","adversary":"","confidence":""}}
"""

    for attempt in range(3):
        try:
            r = requests.post(OLLAMA_URL, json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False
            }, timeout=120)

            if r.status_code == 200:
                return r.json().get("response", "")

        except Exception as e:
            warn(f"Ollama retry {attempt+1}/3 failed: {e}")
            time.sleep(3)

    return ""

# ============================================
# PARSER
# ============================================

def parse_ai(text):
    try:
        text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)

        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            j = match.group()

            j = j.replace("\n", " ")
            j = re.sub(r",\s*}", "}", j)

            return json.loads(j)

    except Exception as e:
        warn(f"Parse error: {e}")

    return None

# ============================================
# FALLBACK
# ============================================

def fallback_decision():
    if not ADVERSARIES:
        return None

    name = list(ADVERSARIES.keys())[0]

    return {
        "analysis": "Fallback mode",
        "adversary": name,
        "confidence": "low"
    }

# ============================================
# MAIN
# ============================================

banner()

while not get_agents():
    warn("Waiting for agent...")
    time.sleep(5)

load_adversaries()

while True:
    try:
        section("Collecting Execution Logs")

        data = extract_execution_data()

        if not data:
            warn("No logs available")
            time.sleep(10)
            continue

        section("AI Analysis")

        ai_raw = ask_ai(data)

        if not ai_raw:
            warn("AI not responding → fallback")
            ai = fallback_decision()
        else:
            print("\n[ RAW AI RESPONSE ]")
            print(ai_raw.strip())

            ai = parse_ai(ai_raw)

            if not ai:
                warn("Parsing failed → fallback")
                ai = fallback_decision()

        analysis = ai.get("analysis", "")
        adv = str(ai.get("adversary", "")).strip()
        conf = normalize_confidence(ai.get("confidence"))

        section("AI Decision")

        print(f"Analysis      : {analysis}")
        print(f"Adversary     : {adv}")
        print(f"Confidence    : {conf}")

        if not adv:
            warn("No adversary → skipped")
            continue

        if adv == LAST_ADVERSARY:
            warn("Repeating adversary → skipped")
            continue

        if conf in ["high", "medium"]:
            if time.time() - LAST_ATTACK_TIME > ATTACK_COOLDOWN:
                launch_attack(adv)
            else:
                warn("Cooldown active")
        else:
            warn("Low confidence → skipped")

        LAST_ADVERSARY = adv

    except KeyboardInterrupt:
        print("\nStopping VAPT Automation...")
        break

    time.sleep(15)