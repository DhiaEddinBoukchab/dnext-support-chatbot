from groq import Groq
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class LLMHandler:
    """Handles Groq LLM interactions with conversation classification"""
    
    def __init__(self, api_key: str, model: str):
        """Initialize Groq client"""
        try:
            self.client = Groq(api_key=api_key)
            self.model = model
            logger.info("✅ Groq client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Groq client: {e}")
            raise
    
    def classify_conversation(self, query: str) -> str:
        """Classify if conversation is casual or technical"""
        classification_prompt = f"""Classify the following user message as either "CASUAL" or "TECHNICAL".

CASUAL examples:
- Greetings: "hello", "hi", "hey", "good morning"
- Small talk: "how are you?", "what's up?", "thanks"
- General questions: "who made you?", "what can you do?"
- Chitchat: "tell me a joke", "what's your name?"

TECHNICAL examples:
- Product questions: "how do I download a dataset?"
- Troubleshooting: "I'm getting an error", "login not working"
- API/Code questions: "show me the API code", "how to authenticate"
- Feature questions: "where is the forecast code?", "how to use TradeMatrix?"

User message: "{query}"

Respond with ONLY one word: CASUAL or TECHNICAL"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": classification_prompt}],
                temperature=0.1,
                max_tokens=10
            )
            classification = response.choices[0].message.content.strip().upper()
            logger.info(f"Conversation classified as: {classification}")
            return classification if classification in ["CASUAL", "TECHNICAL"] else "TECHNICAL"
        except Exception as e:
            logger.error(f"Classification error: {e}")
            return "TECHNICAL"  # Default to technical if classification fails
    
    def generate_response(self, context: str, query: str) -> str:
        """Generate response using LLM with conversation-aware prompts"""
        # First, classify the conversation type
        conversation_type = self.classify_conversation(query)
        
        # Generate response based on type
        if conversation_type == "CASUAL":
            prompt = self._create_casual_prompt(query)
        else:
            prompt = self._create_technical_prompt(context, query)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3 if conversation_type == "CASUAL" else 0.2,
                max_tokens=800 if conversation_type == "CASUAL" else 1500
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            return f"❌ Error generating response: {str(e)}"
    
    def _create_casual_prompt(self, query: str) -> str:
        """Create prompt for casual conversation"""
        return f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You are Dnext Assistant, a friendly and helpful AI assistant for the Dnext platform.

<|start_header_id|>user<|end_header_id|>
{query}

<|start_header_id|>assistant<|end_header_id|>
**Instructions:**
- Respond naturally and friendly like a human support agent
- Be warm, personable, and conversational
- Use emojis appropriately (😊, 👋, 🎉, etc.)
- Keep responses brief and engaging
- If they ask what you can help with, mention you can help with:
  • Dataset downloads and access
  • API usage and authentication
  • TradeMatrix features
  • Troubleshooting issues
  • General platform navigation
- Always stay helpful and positive

Now respond naturally:"""
    
    def _create_technical_prompt(self, context: str, query: str) -> str:
        """Create optimized prompt for technical questions"""
        return f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You are Dnext Assistant, a technical support expert providing precise, actionable solutions.

<|start_header_id|>user<|end_header_id|>
**Customer Question:**
{query}

**Technical Documentation (for reference only):**
{context}

<|start_header_id|>assistant<|end_header_id|>
**Response Guidelines:**

1. **CORE RULES:**
   - Answer as an expert support agent with direct knowledge
   - NEVER say "based on documentation" or "according to the context"
   - NEVER mention you're referencing any source
   - Speak confidently from expertise
   - Stick ONLY to information in the documentation provided
   - If the documentation doesn't cover it, say: "For specific details about this, contact support@dnext.io"

2. **CODE RESPONSES:**
   - Provide COMPLETE, WORKING code examples
   - Format: ```python (full working code) ```
   - Include all imports and setup
   - Add brief inline comments
   - Make it copy-paste ready
   
   Example:
   ```python
   # Complete working example
   import requests
   
   api_key = "your_api_key"
   response = requests.get(url, headers={{"Authorization": f"Bearer {{api_key}}"}})
   print(response.json())
   ```

3. **STEP-BY-STEP GUIDES:**
   - Use numbered steps (1., 2., 3.)
   - Be specific and actionable
   - Include prerequisites
   - Mention common pitfalls

4. **FORMATTING:**
   - Use **bold** for important terms
   - Use bullet points (•) for lists
   - Keep paragraphs concise
   - Separate sections clearly

5. **TONE:**
   - Professional and technical
   - Clear and direct
   - Minimal emojis (only ✅ ❌ if needed)
   - Focus on solutions

Now provide your technical answer:"""