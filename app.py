from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from google import genai

app = Flask(__name__)
CORS(app)  # Enable CORS to allow requests from different origins

@app.route('/evaluate-essay', methods=['POST'])
def evaluate_essay():
    try:
        data = request.json
        rubrics_criteria = data.get('rubrics', '')
        essay = data.get('essay', '')
        api_key = data.get('api_key', '')
        
        # Validate inputs
        if not rubrics_criteria or not essay:
            return jsonify({"error": "Rubrics criteria and essay are required"}), 400
        
        if not api_key:
            return jsonify({"error": "API key is required"}), 400
        
        # Initialize Google AI client
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
        
        # Call Google Gemini API
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=full_prompt
        )
        
        # Try to parse the response as JSON
        try:
            result = json.loads(response.text)
            return jsonify(result)
        except json.JSONDecodeError:
            # If the response is not JSON, return it as is with a note
            return jsonify({
                "raw_response": response.text,
                "note": "The AI response was not in valid JSON format. You may need to adjust your rubrics formatting."
            })
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
