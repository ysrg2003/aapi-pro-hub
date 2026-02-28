#!/usr/bin/env python3
"""
AAPI Pro Hub - مولد الكود (AI-2)
يحول SPEC إلى أكواد برمجية
يدعم وضعين:
- create: إنشاء ملفات جديدة
- patch: تعديل ملفات موجودة بدقة (بدون إعادة كتابة كاملة)
"""

import json
import argparse
import os
from pathlib import Path
from typing import Dict, List, Any

class CodeGenerator:
    """مولد الكود - يحول SPEC لكود برمجي"""
    
    def __init__(self):
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, str]:
        """قوالب الكود الأساسية"""
        return {
            'python': {
                'main': '''#!/usr/bin/env python3
"""
{title}
{description}
"""

import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description='{title}')
    parser.add_argument('--input', help='ملف الإدخال')
    parser.add_argument('--output', help='ملف الإخراج')
    args = parser.parse_args()
    
    # الكود الرئيسي هنا
    print("Hello, World!")

if __name__ == '__main__':
    main()
''',
                'requirements': '# متطلبات المشروع\n# أضف التبعيات هنا\n',
            },
            'javascript': {
                'main': '''// {title}
// {description}

const args = process.argv.slice(2);
console.log("Hello, World!");

module.exports = {{}};
''',
                'package': '''{{
  "name": "{project_name}",
  "version": "1.0.0",
  "description": "{description}",
  "main": "index.js",
  "scripts": {{
    "start": "node index.js",
    "test": "echo \\"Error: no test specified\\" && exit 1"
  }},
  "keywords": [],
  "author": "",
  "license": "MIT"
}}
''',
            },
            'html': {
                'index': '''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <h1>{title}</h1>
    <script src="script.js"></script>
</body>
</html>
''',
                'style': '''/* {title} Styles */
* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

body {{
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: #f5f5f5;
    min-height: 100vh;
}}
''',
                'script': '''// {title} - Script
console.log("Hello from {title}!");
''',
            },
                           'main': 'typescript': {
 '''// {title}
// {description}

function main(): void {{
    console.log("Hello, World!");
}}

main();
''',
                'tsconfig': '''{{
  "compilerOptions": {{
    "target": "ES2020",
    "module": "commonjs",
    "strict": true,
    "esModuleInterop": true
  }}
}}
''',
            },
            'go': {
                'main': '''package main

import "fmt"

func main() {{
    fmt.Println("Hello, World!")
}}
''',
            },
            'rust': {
                'main': '''// {title}
// {description}

fn main() {{
    println!("Hello, World!");
}}
''',
                'cargo': '''[package]
name = "{project_name}"
version = "0.1.0"
edition = "2021"

[dependencies]
''',
            },
        }
    
    def generate(self, spec: Dict[str, Any], mode: str = 'create', existing_files: Dict[str, str] = None) -> Dict[str, Any]:
        """
        توليد الكود بناءً على SPEC
        
        Args:
            spec: مواصفات SPEC
            mode: وضع التشغيل (create أو patch)
            existing_files: ملفات موجودة للتعديل
        
        Returns:
            dict with files_created, files_modified, patches
        """
        language = spec.get('language', 'python')
        files_needed = spec.get('files_needed', [])
        original_prompt = spec.get('original_prompt', '')
        
        result = {
            'mode': mode,
            'language': language,
            'files_created': [],
            'files_modified': [],
            'patches': [],
            'build_commands': spec.get('build_commands', []),
            'test_commands': spec.get('test_commands', []),
        }
        
        if mode == 'create':
            # وضع الإنشاء - إنشاء ملفات جديدة
            for file_name in files_needed:
                content = self._generate_file_content(file_name, language, original_prompt, spec)
                result['files_created'].append({
                    'path': file_name,
                    'content': content
                })
        
        elif mode == 'patch' and existing_files:
            # وضع التعديل - تعديلات دقيقة فقط
            result['patches'] = self._generate_patches(
                original_prompt, 
                existing_files, 
                spec
            )
        
        return result
    
    def _generate_file_content(self, file_name: str, language: str, prompt: str, spec: Dict) -> str:
        """توليد محتوى ملف واحد"""
        
        # استخدام القالب المناسب
        templates = self.templates.get(language, self.templates['python'])
        
        # استخراج اسم المشروع
        project_name = self._extract_project_name(prompt, file_name)
        
        # استخراج الوصف
        description = prompt[:100] if prompt else 'مشروع برمجي'
        
        data = {
            'title': project_name,
            'description': description,
            'project_name': project_name.lower().replace(' ', '-'),
        }
        
        # اختيار القالب المناسب
        if file_name.endswith('.py'):
            template = templates.get('main', templates.get('python', {}).get('main', ''))
        elif file_name == 'requirements.txt':
            template = templates.get('requirements', '')
        elif file_name.endswith('.js'):
            template = templates.get('main', '')
        elif file_name == 'package.json':
            template = templates.get('package', '')
        elif file_name.endswith('.html'):
            template = templates.get('index', '')
        elif file_name.endswith('.css'):
            template = templates.get('style', '')
        elif file_name == 'tsconfig.json':
            template = templates.get('tsconfig', '')
        elif file_name.endswith('.go'):
            template = templates.get('main', '')
        elif file_name.endswith('.rs'):
            template = templates.get('main', '')
        else:
            template = '# {title}\n# {description}\n\n'
        
        # تعبئة القالب
        for key, value in data.items():
            template = template.replace(f'{{{key}}}', value)
        
        return template
    
    def _extract_project_name(self, prompt: str, file_name: str) -> str:
        """استخراج اسم المشروع من البرومبت"""
        # استخراج من البرومبت
        words = prompt.split()
        if len(words) >= 2:
            return words[0].title()
        
        # أو من اسم الملف
        return Path(file_name).stem.replace('_', ' ').title()
    
    def _generate_patches(self, prompt: str, existing_files: Dict[str, str], spec: Dict) -> List[Dict]:
        """
        توليد تعديلات دقيقة (Patches)
        
        صيغة التعديل:
        - AFTER line X: insert Y
        - REPLACE lines X-Y with Z
        - DELETE lines X-Y
        """
        patches = []
        
        # تحليل ما يحتاج تعديل
        # هذه مجرد示例 - في الواقع سيُستدعى AI لتحديد التعديلات
        
        patch_example = {
            'file': 'main.py',
            'operation': 'insert',  # insert | replace | delete
            'after_line': 10,
            'content': '# كود مضاف حديثاً',
            'reason': 'إضافة ميزة جديدة',
        }
        
        patches.append(patch_example)
        
        return patches
    
    def write_files(self, files: List[Dict], output_dir: str):
        """كتابة الملفات إلى القرص"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for file_info in files:
            file_path = output_path / file_info['path']
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(file_info['content'])
            
            print(f"  ✓ Created: {file_info['path']}")


def main():
    parser = argparse.ArgumentParser(description='مولد الكود - AI-2')
    parser.add_argument('--spec', required=True, help='ملف SPEC')
    parser.add_argument('--output', required=True, help='مجلد الإخراج')
    parser.add_argument('--mode', default='create', choices=['create', 'patch'], help='وضع التشغيل')
    parser.add_argument('--target-repo', help='المستودع المستهدف')
    
    args = parser.parse_args()
    
    # تحميل SPEC
    with open(args.spec, 'r', encoding='utf-8') as f:
        spec = json.load(f)
    
    # تحميل الملفات الموجودة (للوضع patch)
    existing_files = {}
    if args.mode == 'patch' and args.target_repo:
        repo_path = Path(args.target_repo)
        if repo_path.exists():
            for py_file in repo_path.rglob('*.py'):
                with open(py_file, 'r', encoding='utf-8') as f:
                    existing_files[str(py_file)] = f.read()
    
    # توليد الكود
    generator = CodeGenerator()
    result = generator.generate(spec, mode=args.mode, existing_files=existing_files)
    
    # كتابة الملفات
    if result['files_created']:
        generator.write_files(result['files_created'], args.output)
    
    # حفظ معلومات result
    result_file = Path(args.output) / 'generation_result.json'
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ تم التوليد بنجاح!")
    print(f"   الملفات المنشأة: {len(result['files_created'])}")
    print(f"   الملفات المعدلة: {len(result['files_modified'])}")
    print(f"   التعديلات (patches): {len(result['patches'])}")


if __name__ == '__main__':
    main()
