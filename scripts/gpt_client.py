#!/usr/bin/env python3
"""
AAPI Pro Hub - استدعاء ChatGPT API
"""

import os
import json
import sys

def call_chatgpt():
    """استدعاء ChatGPT API"""
    
    try:
        import openai
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("Error: OPENAI_API_KEY not set")
            sys.exit(1)
        
        openai.api_key = api_key
        
        prompt = os.getenv('PROMPT', '')
        request_id = os.getenv('REQUEST_ID', 'unknown')
        
        response = openai.chat.completions.create(
            model='gpt-4o',
            messages=[
                {'role': 'system', 'content': 'أنت مساعد برمجي متخصص.'},
                {'role': 'user', 'content': prompt}
            ],
            temperature=0.7,
            max_tokens=4000
        )
        
        result = {
            'request_id': request_id,
            'response': response.choices[0].message.content,
            'model': 'gpt-4o',
            'status': 'success'
        }
        
        with open('gpt_result.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print("Done")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    call_chatgpt()
