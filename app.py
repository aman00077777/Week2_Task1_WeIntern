import os
import uuid
import datetime
from typing import Optional
from flask import Flask, render_template, request, jsonify, session, send_file
from nlp_engine import CodePulseNLPEngine

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()

# Global NLP Engine instance
engine: Optional[CodePulseNLPEngine] = None

LOGS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

def setup_chatbot_engine():
    global engine
    intents_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "intents.json")
    engine = CodePulseNLPEngine(intents_file)

def resolve_log_path(session_id):
    return os.path.join(LOGS_DIR, f"session_{session_id}.txt")

def log_conversation_history(session_id, user_message, bot_response, intent, confidence):
    filepath = resolve_log_path(session_id)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Check if file is new to write a header
    is_new = not os.path.exists(filepath)
    
    with open(filepath, "a", encoding="utf-8") as f:
        if is_new:
            f.write(f"=== CodePulse AI Chat Session: {session_id} ===\n")
            f.write(f"Started at: {timestamp}\n")
            f.write("=" * 50 + "\n\n")
            
        f.write(f"[{timestamp}] USER: {user_message}\n")
        f.write(f"[{timestamp}] BOT (Intent: {intent}, Conf: {confidence:.2f}): {bot_response}\n")
        f.write("-" * 50 + "\n")

@app.route("/")
def index():
    # Initialize a new session ID if it doesn't exist
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())
        session["context"] = None
        session["message_count"] = 0
        session["start_time"] = datetime.datetime.now().isoformat()
    return render_template("index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    global engine
    if engine is None:
        setup_chatbot_engine()
    assert engine is not None
        
    # Lazy initialization of session variables if user bypassed index route
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())
        session["context"] = None
        session["message_count"] = 0
        session["start_time"] = datetime.datetime.now().isoformat()
        
    data = request.json or {}
    user_message = data.get("message", "").strip()
    
    if not user_message:
        return jsonify({"error": "Empty message"}), 400
        
    # Process message using NLP engine
    current_context = session.get("context")
    result = engine.handle_message(user_message, session_context=current_context)
    
    # Update session context
    session["context"] = result["context"]
    session["message_count"] = session.get("message_count", 0) + 1
    
    # Log the interaction
    log_conversation_history(
        session["session_id"],
        user_message,
        result["response"],
        result["intent"],
        result["confidence"]
    )
    
    return jsonify({
        "response": result["response"],
        "intent": result["intent"],
        "confidence": result["confidence"],
        "context": result["context"],
        "message_count": session["message_count"]
    })

@app.route("/api/intents", methods=["GET"])
def get_intents():
    global engine
    if engine is None:
        setup_chatbot_engine()
    assert engine is not None
        
    # Return a simplified list of supported intents for UI sidebar display
    intents_summary = []
    for intent in engine.intents_data["intents"]:
        # first sentence of first response
        description = intent["responses"][0].split(".")[0] + "."
        intents_summary.append({
            "tag": intent["tag"],
            "description": description
        })
    return jsonify(intents_summary)

@app.route("/api/stats", methods=["GET"])
def get_stats():
    if "session_id" not in session:
        return jsonify({"error": "No active session"}), 400
        
    start_time = datetime.datetime.fromisoformat(session["start_time"])
    elapsed = datetime.datetime.now() - start_time
    minutes = int(elapsed.total_seconds() // 60)
    seconds = int(elapsed.total_seconds() % 60)
    duration_str = f"{minutes:02d}:{seconds:02d}"
    
    return jsonify({
        "session_id": session["session_id"],
        "message_count": session.get("message_count", 0),
        "active_context": session.get("context") or "None",
        "duration": duration_str
    })

@app.route("/api/logs", methods=["GET"])
def get_logs():
    if "session_id" not in session:
        return jsonify({"logs": "No active session logs."})
        
    filepath = resolve_log_path(session["session_id"])
    if not os.path.exists(filepath):
        return jsonify({"logs": "No messages logged in this session yet."})
        
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    return jsonify({"logs": content})

@app.route("/api/logs/download", methods=["GET"])
def download_logs():
    if "session_id" not in session:
        return "No active session logs", 400
        
    filepath = resolve_log_path(session["session_id"])
    if not os.path.exists(filepath):
        return "No log file found", 404
        
    return send_file(
        filepath,
        as_attachment=True,
        download_name=f"codepulse_session_{session['session_id'][:8]}.txt",
        mimetype="text/plain"
    )

@app.route("/api/reset", methods=["POST"])
def reset():
    # Clear the session
    session.clear()
    
    # Initialize a new session
    session["session_id"] = str(uuid.uuid4())
    session["context"] = None
    session["message_count"] = 0
    session["start_time"] = datetime.datetime.now().isoformat()
    
    return jsonify({"status": "Session reset successfully", "session_id": session["session_id"]})

if __name__ == "__main__":
    setup_chatbot_engine()
    app.run(debug=True, host="127.0.0.1", port=5000)
