import json
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics.pairwise import cosine_similarity

class CodePulseNLPEngine:
    def __init__(self, intents_path="intents.json"):
        self.intents_path = intents_path
        self.intents_data = None
        self.vectorizer = None
        self.classifier = None
        self.patterns = []
        self.tags = []
        self.intent_responses_map = {}
        self.intent_context_set_map = {}
        self.intent_context_clear_map = {}
        self.intent_context_responses_map = {}
        self.training_vectors = None
        
        self.load_intents_data()
        self.train_engine()

    def clean_and_tokenize(self, text):
        # Convert to lowercase and clean punctuation
        text = text.lower().strip()
        text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
        return text

    def load_intents_data(self):
        with open(self.intents_path, "r", encoding="utf-8") as f:
            self.intents_data = json.load(f)
            
        for intent in self.intents_data["intents"]:
            tag = intent["tag"]
            self.intent_responses_map[tag] = intent["responses"]
            
            if "context_set" in intent:
                self.intent_context_set_map[tag] = intent["context_set"]
            if "context_clear" in intent:
                self.intent_context_clear_map[tag] = intent["context_clear"]
            if "context_responses" in intent:
                self.intent_context_responses_map[tag] = intent["context_responses"]
                
            for pattern in intent["patterns"]:
                self.patterns.append(pattern)
                self.tags.append(tag)

    def train_engine(self):
        # Custom stop words list to remove grammatical noise but keep intent question words
        self.stop_words = [
            "the", "is", "a", "an", "and", "or", "to", "of", "in", "at", "by", 
            "this", "that", "there", "has", "have", "been", "was", "were", "be", 
            "do", "does", "did", "i", "my", "about", "with", "here"
        ]
        
        # Initialize Vectorizer with custom preprocessor and stop words
        self.vectorizer = TfidfVectorizer(
            preprocessor=self.clean_and_tokenize, 
            stop_words=self.stop_words,
            ngram_range=(1, 2)
        )
        
        # Fit and transform patterns
        self.training_vectors = self.vectorizer.fit_transform(self.patterns)
        
        # Initialize and fit Logistic Regression
        # We use low regularization (C=10) since patterns are distinct and few
        self.classifier = LogisticRegression(C=10.0, max_iter=1000)
        self.classifier.fit(self.training_vectors, self.tags)

    def predict_intent(self, sentence, similarity_threshold=0.28, confidence_threshold=0.30):
        """
        Classifies a user query into one of the intent tags.
        Uses a combination of Logistic Regression probability and Cosine Similarity.
        """
        preprocessed = self.clean_and_tokenize(sentence)
        if not preprocessed.strip():
            return "fallback", 0.0

        # Vectorize the input sentence
        input_vector = self.vectorizer.transform([sentence])
        
        # 1. Compute Cosine Similarity with all training patterns
        sim_scores = cosine_similarity(input_vector, self.training_vectors).flatten()
        max_sim_idx = np.argmax(sim_scores)
        max_sim = sim_scores[max_sim_idx]
        closest_tag_by_sim = self.tags[max_sim_idx]
        
        # 2. Get Logistic Regression Probabilities
        proba = self.classifier.predict_proba(input_vector)[0]
        max_proba_idx = np.argmax(proba)
        max_proba = proba[max_proba_idx]
        predicted_tag = self.classifier.classes_[max_proba_idx]
        
        # Determine fallback status
        is_fallback = False
        
        # OOV (Out-Of-Vocabulary) words check to handle off-topic/meaningless queries
        # Bypassed if similarity is high, indicating a strong direct match (e.g. >= 0.50)
        if max_sim < 0.50:
            stop_words_set = set(self.stop_words or [])
            words = [w for w in preprocessed.split() if w not in stop_words_set]
            if words:
                vocab = getattr(self.vectorizer, 'vocabulary_', {})
                oov_words = [w for w in words if w not in vocab]
                oov_ratio = len(oov_words) / len(words)
                if oov_ratio > 0.50 or (len(oov_words) >= 2 and oov_ratio >= 0.40):
                    is_fallback = True

        if not is_fallback:
            # Low confidence check
            if max_sim < 0.22:
                is_fallback = True
            elif max_proba < 0.32 and max_sim < 0.50:
                is_fallback = True
                
        if is_fallback:
            return "fallback", float(max_sim)
            
        # If the similarity check is very high, prefer similarity-based tag to avoid logistic regression bias
        if max_sim > 0.6:
            return closest_tag_by_sim, float(max_sim)
            
        return predicted_tag, float(max_proba)

    def retrieve_reply(self, tag, session_context=None):
        """
        Retrieves a response for a tag. Accounts for multi-turn session context.
        """
        # If the tag has context responses and a session context is active, return that specific response
        if tag in self.intent_context_responses_map and session_context:
            context_resps = self.intent_context_responses_map[tag]
            if session_context in context_resps:
                return context_resps[session_context]
                
        # Default response selection (random choice or first response)
        responses = self.intent_responses_map.get(tag, ["I am not sure how to answer that."])
        
        # Pick one response (for consistency, we can choose the first one or rotate, let's use the first one)
        # We can also use simple selection based on length or index.
        return responses[0]

    def handle_message(self, message, session_context=None):
        """
        Processes a full user message, updates context, and returns a response structure.
        """
        tag, confidence = self.predict_intent(message)
        
        if tag == "fallback":
            response = "I'm sorry, I didn't quite catch that. I am a coding assistant, so I can help with Python, SQL, Git, APIs, Web Development, and interview preparation. Could you rephrase your question?"
            new_context = session_context # keep old context
        else:
            response = self.retrieve_reply(tag, session_context)
            
            # Determine new context state
            new_context = session_context
            if tag in self.intent_context_set_map:
                new_context = self.intent_context_set_map[tag]
            elif tag in self.intent_context_clear_map:
                new_context = None
                
        return {
            "intent": tag,
            "confidence": confidence,
            "response": response,
            "context": new_context
        }

if __name__ == "__main__":
    # Test script output
    engine = CodePulseNLPEngine("intents.json")
    print("NLP Engine trained successfully!")
    print(engine.handle_message("hello"))
    print(engine.handle_message("how do i write python code"))
    print(engine.handle_message("give me an example", session_context="python_context"))
    print(engine.handle_message("random gibberish that doesn't match"))
