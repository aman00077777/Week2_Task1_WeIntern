import sys
from nlp_engine import CodePulseNLPEngine

def main():
    print("\n" + "=" * 60)
    print("      CodePulse AI - Interactive CLI Developer Assistant")
    print("=" * 60)
    print("Ask your programming, Git, SQL, API, or debugging questions below.")
    print("Topic follow-ups supported: 'give me an example' or 'tell me more'.")
    print("Type 'exit', 'quit', or 'bye' to terminate the session.\n")
    
    try:
        # Load the rebranded NLP engine
        engine = CodePulseNLPEngine("intents.json")
    except Exception as e:
        print(f"Error loading intents data: {e}")
        sys.exit(1)
        
    context = None
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break
            
        if not user_input:
            continue
            
        if user_input.lower() in ["exit", "quit", "bye"]:
            # Process final message to get goodbye response
            res = engine.handle_message(user_input, session_context=context)
            print(f"\nCodePulse: {res['response']}")
            break
            
        # Process user query
        res = engine.handle_message(user_input, session_context=context)
        
        # Update context
        context = res["context"]
        
        # Display bot response
        print(f"CodePulse: {res['response']}")

if __name__ == "__main__":
    # Prevent creating pycache bytecode folder on run
    sys.dont_write_bytecode = True
    main()
