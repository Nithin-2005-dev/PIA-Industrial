# Getting Started with PIA Industrial

This guide covers the complete setup of the PIA Industrial backend and frontend.

## Prerequisites

- **Python:** 3.10 or higher
- **Node.js:** 18 or higher (for frontend UI)
- **OS:** Windows, macOS, or Linux

## 1. Clone the Repository

```bash
git clone https://github.com/your-org/pia-industrial.git
cd pia-industrial
```

## 2. Backend Setup

The backend is built with FastAPI. It handles document ingestion, the knowledge graph, and the intelligence engines.

```bash
cd backend
python -m venv venv
```

Activate the virtual environment:
- **Windows:** `venv\Scripts\activate`
- **macOS/Linux:** `source venv/bin/activate`

Install dependencies:
```bash
pip install -r requirements.txt
```

*(Note: The current prototype uses an in-memory NetworkX graph and a local SQLite database, so no external database installation is required.)*

## 3. Environment Configuration

Create your `.env` file in the `backend/` directory based on the `.env.example`:

```bash
cp .env.example .env
```

For more details on configuration, see [Configuration Guide](CONFIGURATION.md).

## 4. Load the Demo Dataset

To populate the system with the mock industrial assets and the P-101 pump anomaly scenario, run the demo seeder:

```bash
python -m scripts.demo.demo_seeder
```
*(This command will read the industrial data from `data/demo/p101/` and insert it into the SQLite event store and Knowledge Graph.)*

## 5. Running the Backend Server

Start the FastAPI server:

```bash
uvicorn app.api.server:app --reload
```
The API will be available at `http://localhost:8000`. 
Interactive API documentation is automatically hosted at `http://localhost:8000/docs`.

## 6. Frontend Setup & Run (Optional)

If you wish to use the graphical Hackathon UI:

Open a new terminal window:
```bash
cd pia-industrial/frontend
npm install
npm run dev
```
The frontend will start at `http://localhost:5173`.

## 7. Verifying the Installation

To verify that the deterministic engines are functioning correctly, you can run the test suite:

```bash
cd backend
python -m pytest tests/
```

If the tests pass, your system is fully operational.

## Troubleshooting

- **ModuleNotFoundError**: Ensure your virtual environment is activated and you are running commands from the `backend/` directory.
- **Port 8000 in use**: If another service is using port 8000, you can start the backend on a different port: `uvicorn app.api.server:app --reload --port 8001`.
