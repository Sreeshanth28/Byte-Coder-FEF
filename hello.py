import requests, json
def fun(question):
    url="https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key=AIzaSyABR_F4iC0L--TeBlPhTEb_ep8A_vPM9GM"
    headers = {
        "Content-Type": "application/json"
    }
    
    # Create the prompt with instructions
    prompt = f"""
    You are a leading buy now pay later provider in the market. Please provide the following information in JSON format without any additional text or explanation in clean text (no bold, no italic, etc):
    
    {{
        "question": "{question}",
        "questionImage_URL": "<url_of_question_image>",
        "answer": "<your_answer_here>",
        "explanation": "<your_explanation_here">
        "answerImage_URL": "<url_of_answer_image>"
    }}
    """

    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }

    # Send the request to the Gemini API
    response = requests.post(url, headers=headers, data=json.dumps(data))

    # Check if the request was successful
    if response.status_code == 200:
        # Extract the attributes from the API response
        response_data = response.json()
        result = response_data['candidates'][0]['content']['parts'][0]['text']
        return result
    
q =  "From the given credit history, please suggest an amount that can be goven to him for bnpl"
print(fun(q))