#!/usr/bin/env python3
"""
AAPI Pro Hub - استدعاء Gemini API
"""

import os
import json
import sys

def call_gemini():
    """استدعاء Gemini API"""
    
    try:
        import google.generativeai as genai
        
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("Error: GEMINI_API_KEY not set")
            sys.exit(1)
        
        genai.configure(api_key=api_key)
        
        prompt = os.getenv('PROMPT', '')
        request_id = os.getenv('REQUEST_ID', 'unknown')
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        
        result = {
            'request_id': request_id,
            'response': response.text,
            'model': 'gemini-1.5-flash',
            'status': 'success'
        }
        
        with open('gemini_result.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print("Done")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    call_gemini()
