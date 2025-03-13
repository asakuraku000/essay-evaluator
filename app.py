from flask import Flask, request, jsonify
from google import genai
import os

app = Flask(__name__)

@app.route('/evaluate', methods=['POST'])
def evaluate_essay():
    # Get data from POST request
    data = request.json
    if not data or 'essay' not in data or 'rubrics_criteria' not in data:
        return jsonify({"error": "Missing required fields: essay and/or rubrics_criteria"}), 400
    
    essay = data['essay']
    rubrics_criteria = data['rubrics_criteria']
    
    # Set up Google Generative AI client
    api_key = os.environ.get('GENAI_API_KEY', "AIzaSyBHvzt_UwTBHhcw3AYV8NSdjiQASNh1vlo")
    client = genai.Client(api_key=api_key)
    
    # Construct prompt
    initiate_prompt = """I need you to act as an expert essay evaluator. Please grade the essay I'll provide based on the following criteria and weights:

CRITERIA:
""" + rubrics_criteria + """

For each criterion:
1. Assign a score from 0-100
2. Provide brief feedback explaining the score (2-3 sentences)
3. Include 1-2 specific suggestions for improvement

Your response should be structured as a JSON object with:
- Individual scores for each criterion
- Feedback and suggestions for each criterion
- Overall weighted score
- General assessment of strengths (2-3 points)
- Areas for improvement (2-3 points)

Here's my essay:

"""
    full_prompt = initiate_prompt + essay + " (Please provide a comprehensive evaluation that maintains high standards while offering constructive feedback.)"
    
    try:
        # Generate content
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=full_prompt
        )
        
        # Return the evaluation results
        return jsonify({"evaluation": response.text})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
