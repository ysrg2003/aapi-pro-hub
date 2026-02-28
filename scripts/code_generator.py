#!/usr/bin/env python3
"""
AAPI Pro Hub - مولد الكود (AI-2)
"""

import json
import os
from pathlib import Path

def generate_code(spec: dict, prompt: str) -> dict:
    """توليد ملفات الكود بناءً على SPEC"""
    
    language = spec.get('language', 'python')
    files_needed = spec.get('files_needed', [])
    
    generated = []
    
    for file in files_needed:
        content = generate_file_content(file, language, prompt)
        
        # إنشاء المجلد
        Path('generated_code').mkdir(exist_ok=True)
        
        # كتابة الملف
        file_path = f'generated_code/{file}'
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        generated.append(file)
        print(f"Created: {file}")
    
    return {'generated': generated}

def generate_file_content(filename: str, language: str, prompt: str) -> str:
    """توليد محتوى الملف"""
    
    if filename == 'main.py':
        return f'''#!/usr/bin/env python3
"""
{prompt}
"""

def main():
    print("Hello from AAPI Pro!")

if __name__ == "__main__":
    main()
'''
    
    elif filename == 'requirements.txt':
        return '# متطلبات المشروع\n'
    
    elif filename == 'index.js':
        return f'''// {prompt}
console.log("Hello from AAPI Pro!");
'''
    
    elif filename == 'package.json':
        return '''{
  "name": "aapi-project",
  "version": "1.0.0",
  "main": "index.js",
  "scripts": {
    "start": "node index.js"
  }
}
'''
    
    elif filename == 'index.html':
        return f'''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>AAPI Pro</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <h1>{prompt}</h1>
    <script src="script.js"></script>
</body>
</html>
'''
    
    elif filename == 'style.css':
        return f'''/* {prompt} */
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: sans-serif; }}
'''
    
    elif filename == 'script.js':
        return f'''// {prompt}
console.log("Loaded!");
'''
    
    elif filename == 'main.go':
        return f'''package main

import "fmt"

func main() {{
    fmt.Println("Hello from AAPI Pro!")
}}
'''
    
    elif filename == 'go.mod':
        return '''module aapi-project

go 1.21
'''
    
    else:
        return f'# {filename}\n'

if __name__ == '__main__':
    # تحميل SPEC
    with open('spec.json', 'r', encoding='utf-8') as f:
        spec = json.load(f)
    
    prompt = os.getenv('PROMPT', spec.get('original_prompt', 'Project'))
    
    result = generate_code(spec, prompt)
    print(f"Generated {len(result['generated'])} files")
