import sys
from nlp_engine import CodePulseNLPEngine

def run_tests():
    # Instantiate the NLP engine
    try:
        engine = CodePulseNLPEngine("intents.json")
    except Exception as e:
        print(f"Error initializing NLP engine: {e}")
        sys.exit(1)
        
    print("\n" + "=" * 105)
    print(" " * 40 + "CODEPULSE CHATBOT TEST SUITE")
    print("=" * 105)
    
    # 21 Diverse test scenarios, including sequential context states
    test_cases = [
        # --- Greetings & Core Bot info ---
        {"input": "Hello there!", "context": None, "expected_intent": "greeting"},
        {"input": "yo", "context": None, "expected_intent": "greeting"},
        {"input": "what is your name?", "context": None, "expected_intent": "bot_identity"},
        {"input": "what features do you support?", "context": None, "expected_intent": "help"},
        
        # --- Python Flow (Stateful check) ---
        {"input": "how do I learn python?", "context": None, "expected_intent": "python_basics"},
        {"input": "give me an example", "context": "python_context", "expected_intent": "context_example"},
        {"input": "tell me more", "context": "python_context", "expected_intent": "context_more"},
        
        # --- Git Flow ---
        {"input": "How does git version control work?", "context": None, "expected_intent": "git_basics"},
        {"input": "show me an example of that", "context": "git_context", "expected_intent": "context_example"},
        
        # --- SQL Flow ---
        {"input": "what is an SQL select query?", "context": None, "expected_intent": "sql_queries"},
        {"input": "give me a code sample", "context": "sql_context", "expected_intent": "context_example"},
        {"input": "elaborate please", "context": "sql_context", "expected_intent": "context_more"},
        
        # --- Web Dev & APIs ---
        {"input": "what is the difference between frontend and backend?", "context": None, "expected_intent": "frontend_vs_backend"},
        {"input": "explain REST APIs", "context": None, "expected_intent": "api_basics"},
        
        # --- Debugging & Interview prep ---
        {"input": "how do I fix my broken python code?", "context": None, "expected_intent": "debug_code"},
        {"input": "give me code to handle division by zero", "context": "debug_context", "expected_intent": "context_example"},
        {"input": "I need help with my coding interview prep", "context": None, "expected_intent": "interview_tips"},
        {"input": "details about that preparation", "context": "interview_context", "expected_intent": "context_more"},
        
        # --- Fallback Handling (Unrecognized queries) ---
        {"input": "what is the meaning of life?", "context": None, "expected_intent": "fallback"},
        {"input": "how do I bake chocolate cookies?", "context": None, "expected_intent": "fallback"},
        {"input": "asdfghjklqwertyuiop", "context": None, "expected_intent": "fallback"},
        
        # --- Goodbye ---
        {"input": "thank you bye", "context": None, "expected_intent": "goodbye"}
    ]
    
    # Run tests
    headers = f"{'#':<3} | {'User Utterance':<35} | {'Active Context':<18} | {'Predicted Intent':<16} | {'Conf/Sim':<8} | {'Fallback':<8}"
    print(headers)
    print("-" * 105)
    
    passed_counts = 0
    fallback_counts = 0
    
    for idx, tc in enumerate(test_cases, 1):
        utterance = tc["input"]
        current_ctx = tc["context"]
        expected = tc["expected_intent"]
        
        # Process through NLP Engine
        res = engine.handle_message(utterance, session_context=current_ctx)
        
        predicted = res["intent"]
        confidence = res["confidence"]
        next_ctx = res["context"]
        is_fallback = "Yes" if predicted == "fallback" else "No"
        
        # Evaluate success
        status = "FAIL"
        if predicted == expected:
            status = "PASS"
            passed_counts += 1
        elif expected == "fallback" and predicted == "fallback":
            status = "PASS"
            passed_counts += 1
            
        if predicted == "fallback":
            fallback_counts += 1
            
        # Truncate utterance to fit in column
        short_utterance = utterance[:32] + "..." if len(utterance) > 32 else utterance
        
        ctx_str = str(current_ctx) if current_ctx else "None"
        row = f"{idx:<3} | {short_utterance:<35} | {ctx_str:<18} | {predicted:<16} | {confidence:.2f}     | {is_fallback:<8} | {status}"
        print(row)
        
    print("-" * 105)
    print(f"Total Cases: {len(test_cases)}")
    print(f"Passed: {passed_counts} / {len(test_cases)} ({passed_counts/len(test_cases)*100:.1f}%)")
    print(f"Triggered Fallbacks: {fallback_counts} cases")
    print("=" * 105 + "\n")
    
if __name__ == "__main__":
    run_tests()
