#!/usr/bin/env python3
"""
AAPI Pro Hub - محلل الطلبات (AI-1)
"""

import json
import os

def analyze_prompt(prompt: str, request_id: str) -> dict:
    """تحليل البرومبت وإنشاء SPEC"""
    
    prompt_lower = prompt.lower()
    
    # تحديد النية
    intent = 'create'
    if any(w in prompt_lower for w in ['عدل', 'تعديل', 'modify', 'update', 'edit']):
        intent = 'modify'
    if any(w in prompt_lower for w in ['حلل', 'analyze', 'فحص']):
        intent = 'analyze'
    
    # تحديد اللغة
    language = 'python'
    if any(w in prompt_lower for w in ['javascript', 'js', 'جافا سكريبت']):
        language = 'javascript'
    elif any(w in prompt_lower for w in ['typescript', 'ts']):
        language = 'typescript'
    elif any(w in prompt_lower for w in ['html', 'صفحة', 'web']):
        language = 'html'
    elif any(w in prompt_lower for w in ['go', 'golang']):
        language = 'go'
    elif any(w in prompt_lower for w in ['rust']):
        language = 'rust'
    
    # تحديد الملفات المطلوبة
    files_needed = []
    if language == 'python':
        files_needed = ['main.py', 'requirements.txt']
    elif language == 'javascript':
        files_needed = ['index.js', 'package.json']
    elif language == 'html':
        files_needed = ['index.html', 'style.css', 'script.js']
    elif language == 'go':
        files_needed = ['main.go', 'go.mod']
    
    spec = {
        'intent': intent,
        'language': language,
        'original_prompt': prompt,
        'files_needed': files_needed,
        'acceptance_criteria': ['الكود خالٍ من أخطاء'],
        'request_id': request_id
    }
    
    return spec

if __name__ == '__main__':
    prompt = os.getenv('PROMPT', '')
    request_id = os.getenv('REQUEST_ID', 'unknown')
    
    if not prompt:
        print("Error: PROMPT not provided")
        exit(1)
    
    spec = analyze_prompt(prompt, request_id)
    
    with open('spec.json', 'w', encoding='utf-8') as f:
        json.dump(spec, f, ensure_ascii=False, indent=2)
    
    print(f"Done: {spec['language']}")
