import json
import logging
from pathlib import Path

from app import ChatbotApp, Config  # Assuming your main script is app.py

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

def generate_responses_for_json(input_file: str, output_file: str):
    """Original function: Generate model responses for each question in a JSON file."""
    
    # Load existing Q&A JSON
    if not Path(input_file).exists():
        logger.error(f"Input file {input_file} does not exist.")
        return
    
    with open(input_file, 'r', encoding='utf-8') as f:
        qa_data = json.load(f)
    
    if not isinstance(qa_data, list):
        logger.error("JSON file should contain a list of Q&A objects.")
        return
    
    # Initialize chatbot
    logger.info("Initializing ChatbotApp...")
    chatbot = ChatbotApp()
    
    updated_data = []
    
    for i, item in enumerate(qa_data, start=1):
        question = item.get("question")
        if not question:
            logger.warning(f"Skipping entry {i}: no question found")
            continue
        
        logger.info(f"Generating model response for question {i}: {question}")
        model_response = chatbot.answer_query(question, history=[])
        
        item["model_response"] = model_response
        updated_data.append(item)
    
    # Save updated JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(updated_data, f, indent=4, ensure_ascii=False)
    
    logger.info(f"✅ Successfully updated JSON with model responses: {output_file}")


# ------------------ New Function ------------------
def generate_responses_from_specific_question(input_file: str, output_file: str, start_question: str):
    """Generate model responses starting from the element with a specific question."""
    
    # Load existing Q&A JSON
    if not Path(input_file).exists():
        logger.error(f"Input file {input_file} does not exist.")
        return
    
    with open(input_file, 'r', encoding='utf-8') as f:
        qa_data = json.load(f)
    
    if not isinstance(qa_data, list):
        logger.error("JSON file should contain a list of Q&A objects.")
        return
    
    # Find the index to start from
    start_index = None
    for idx, item in enumerate(qa_data):
        if item.get("question") == start_question:
            start_index = idx
            break
    
    if start_index is None:
        logger.error(f"Start question not found in JSON: '{start_question}'")
        return
    
    logger.info(f"Starting from question index {start_index + 1}: {start_question}")
    
    # Initialize chatbot
    chatbot = ChatbotApp()
    
    updated_data = qa_data[:start_index]  # Keep previous items unchanged
    
    for i, item in enumerate(qa_data[start_index:], start=start_index + 1):
        question = item.get("question")
        if not question:
            logger.warning(f"Skipping entry {i}: no question found")
            updated_data.append(item)
            continue
        
        logger.info(f"Generating model response for question {i}: {question}")
        model_response = chatbot.answer_query(question, history=[])
        
        item["model_response"] = model_response
        updated_data.append(item)
    
    # Save updated JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(updated_data, f, indent=4, ensure_ascii=False)
    
    logger.info(f"✅ Successfully updated JSON with model responses: {output_file}")

def generate_responses_from_range(input_file: str, output_file: str, start_question: str, end_question: str = None):
    """
    Generate model responses for questions in JSON starting from a specific question 
    up to (and including) an optional end question.
    
    Parameters:
        input_file: str - Path to input JSON file
        output_file: str - Path to save updated JSON
        start_question: str - Question to start processing from
        end_question: str - Optional question to stop at (inclusive)
    """
    # Load JSON
    if not Path(input_file).exists():
        logger.error(f"Input file {input_file} does not exist.")
        return

    with open(input_file, 'r', encoding='utf-8') as f:
        qa_data = json.load(f)

    if not isinstance(qa_data, list):
        logger.error("JSON file should contain a list of Q&A objects.")
        return

    # Find start index
    start_index = next((i for i, item in enumerate(qa_data) if item.get("question") == start_question), None)
    if start_index is None:
        logger.error(f"Start question not found: '{start_question}'")
        return

    # Find end index
    end_index = None
    if end_question:
        end_index = next((i for i, item in enumerate(qa_data) if item.get("question") == end_question), None)
        if end_index is None:
            logger.warning(f"End question not found: '{end_question}', will process until the last question")
            end_index = len(qa_data) - 1

    else:
        end_index = len(qa_data) - 1

    logger.info(f"Processing questions from index {start_index + 1} to {end_index + 1}")

    # Initialize chatbot
    chatbot = ChatbotApp()

    updated_data = qa_data[:start_index]  # Keep previous items unchanged

    # Process questions in range
    for i, item in enumerate(qa_data[start_index:end_index + 1], start=start_index + 1):
        question = item.get("question")
        if not question:
            logger.warning(f"Skipping entry {i}: no question found")
            updated_data.append(item)
            continue

        logger.info(f"Generating model response for question {i}: {question}")
        model_response = chatbot.answer_query(question, history=[])
        item["model_response"] = model_response
        updated_data.append(item)

    # Append remaining items if any after end_index
    if end_index + 1 < len(qa_data):
        updated_data.extend(qa_data[end_index + 1:])

    # Save updated JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(updated_data, f, indent=4, ensure_ascii=False)

    logger.info(f"✅ Successfully updated JSON with model responses: {output_file}")

if __name__ == "__main__":
    input_json = "q&a.json"
    output_json = "q&a_with_remaining_part.json"
    
    # Call the new function starting from the specific question
    #start_question = "How do I configure port terms in freight estimates?"
    start_question = "Why is my Bulk Calculate operation failing?"
    end_question = "What is the Summary Table in Trade Matrix?"

    generate_responses_from_range(input_json, output_json, start_question, end_question)
    #generate_responses_for_json(input_json, output_json)
