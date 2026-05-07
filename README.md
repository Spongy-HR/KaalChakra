# KaalChakra
KaalChakra currently works as an AI-assisted attack optimization platform. It analyzes attack logs and failures from the attack engine, identifies why techniques failed, suggests improved adversary strategies, and automates re-simulation with optimized attack paths. The project is still under active development with more features planned.

# Setup and Execution Workflow

After installing Caldera
 on the system, navigate to the conf directory inside the Caldera installation folder. Open the default YAML configuration file and modify the following values to allow remote agent communication and proper local network accessibility:

app.contact.http: http://YOUR_IP:8888
app.contact.websocket: YOUR_IP:7012
host: 0.0.0.0

Replace YOUR_IP with the local IP address of the host machine. These changes allow Caldera to listen on all interfaces and enable target systems or agents to connect to the server properly.

Create and Activate Python Virtual Environment

Before running the project, create and activate a Python virtual environment.

Step 1 — Create Virtual Environment
py -3.10 -m venv venv
Step 2 — Activate Virtual Environment
.\venv\Scripts\Activate.ps1
Install Required Dependencies
Upgrade pip
python -m pip install --upgrade pip
Install Project Requirements
pip install -r requirements.txt
Install Docker Module
python -m pip install docker
Start Caldera Server

Run the following command inside the Caldera directory:

python server.py --insecure

After execution, the Caldera server will start locally.

Start Ollama Server

Open a new terminal tab and run:

ollama serve

This starts the local Ollama AI server.

To verify that Ollama is running correctly, open the browser and visit:

http://127.0.0.1

If the server responds successfully, Ollama is active and ready.

Run the Python Integration Script

Open another terminal inside the project directory and execute:

python main.py

This script connects the local Ollama AI model with the locally running Caldera server. It continuously collects attack logs, execution results, and adversary activity from Caldera and displays the AI analysis process through a CLI interface.

Attack Execution Workflow
Open the Caldera dashboard in the browser.
Deploy and connect an agent to the target system.
Launch an adversary attack simulation.
Wait for logs and execution results to appear in the CLI.

The AI model will continuously analyze the attack results in real time.

If the attack executes successfully, the AI simply monitors the process.
If certain attack techniques or adversary actions fail, the AI analyzes the failure, identifies possible reasons, suggests improved techniques or adversary strategies, and automatically triggers optimized attack execution through Caldera.

This creates an automated attack-analysis-improvement loop between the BAS engine and the AI system.
