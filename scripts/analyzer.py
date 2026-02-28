#!/usr/bin/env python3
"""
AAPI Pro Hub - محلل الطلبات (AI-1)
يُحلل برومبت المستخدم ويُنشئ SPEC مُنظَّم قابل للاختبار
"""

import json
import argparse
import os
import re
from pathlib import Path

# محاكاة استدعاء API (يمكن استبدالها بـ ChatGPT/Gemini فعلي)
class RequestAnalyzer:
    """محلل الطلبات - يفهم ماذا يريد المستخدم"""
    
    def __init__(self):
        self.intents = {
            'create': ['أنشئ', 'اكتب', 'صنع', 'build', 'create', 'write', 'make'],
            'modify': ['عدل', 'أضف', 'غير', 'تغيير', 'modify', 'add', 'update', 'change', 'edit'],
            'analyze': ['حلل', 'افحص', 'راجع', 'analyze', 'check', 'review'],
            'debug': ['أصلح', 'solve', 'fix', 'debug', 'اصلح'],
            'deploy': ['نشر', 'deploy', 'شغل'],
        }
        
        self.languages = {
            'python': ['python', 'بايثون', 'py', 'pip'],
            'javascript': ['javascript', 'js', 'جافاسكريبت', 'node'],
            'typescript': ['typescript', 'ts', 'تايب سكريبت'],
            'html': ['html', 'اتش تي ام ال', 'صفحة'],
            'css': ['css', 'ستايل', 'تنسيق'],
            'java': ['java', 'جافا'],
            'go': ['go', 'golang', 'جو'],
            'rust': ['rust', 'رست'],
            'c++': ['c++', 'cpp', 'سي++'],
            'csharp': ['c#', 'csharp', 'سي شارب'],
            'ruby': ['ruby', 'روبي'],
            'php': ['php', 'بي اتش بي'],
            'swift': ['swift', 'سويفت'],
            'kotlin': ['kotlin', 'كوتلن'],
        }
        
        self.frameworks = {
            'django': ['django', 'جانغو'],
            'flask': ['flask', 'فلاسك'],
            'fastapi': ['fastapi', 'فاست ابي'],
            'react': ['react', 'ريأكت'],
            'vue': ['vue', 'فيو'],
            'angular': ['angular', 'أنجولار'],
            'nextjs': ['nextjs', 'next.js', 'نيكست'],
            'express': ['express', 'إكسبريس'],
            'spring': ['spring', 'سبرينغ'],
            'laravel': ['laravel', 'لارافيل'],
        }
    
    def analyze(self, prompt: str) -> dict:
        """تحليل البرومبت وإنشاء SPEC مُنظَّم"""
        
        prompt_lower = prompt.lower()
        
        # 1. تحديد النية (Intent)
        intent = self._detect_intent(prompt_lower)
        
        # 2. تحديد اللغة
        language = self._detect_language(prompt_lower)
        
        # 3. تحديد الإطار (إن وُجد)
        framework = self._detect_framework(prompt_lower)
        
        # 4. استخراج الملفات المطلوبة
        files_needed = self._extract_files(prompt, language, intent)
        
        # 5. إنشاء acceptance criteria
        acceptance_criteria = self._generate_acceptance_criteria(prompt, intent)
        
        # 6. تحديد أوامر البناء والاختبار
        build_commands = self._get_build_commands(language, framework)
        test_commands = self._get_test_commands(language, framework)
        
        # 7. إنشاء SPEC شامل
        spec = {
            "intent": intent,
            "language": language,
            "framework": framework or "none",
            "original_prompt": prompt,
            "files_needed": files_needed,
            "acceptance_criteria": acceptance_criteria,
            "build_commands": build_commands,
            "test_commands": test_commands,
            "strict_mode": True,  # تفعيل وضع التنفيذ الدقيق
            "modification_policy": "patch_only",  # تعديلات دقيقة فقط
        }
        
        return spec
    
    def _detect_intent(self, prompt: str) -> str:
        """اكتشاف نية المستخدم"""
        for intent, keywords in self.intents.items():
            for kw in keywords:
                if kw in prompt:
                    return intent
        return "create"  # الافتراضي
    
    def _detect_language(self, prompt: str) -> str:
        """اكتشاف لغة البرمجة"""
        for lang, keywords in self.languages.items():
            for kw in keywords:
                if kw in prompt:
                    return lang
        return "python"  # الافتراضي
    
    def _detect_framework(self, prompt: str) -> str | None:
        """اكتشاف الإطار"""
        for fw, keywords in self.frameworks.items():
            for kw in keywords:
                if kw in prompt:
                    return fw
        return None
    
    def _extract_files(self, prompt: str, language: str, intent: str) -> list:
        """استخراج الملفات المطلوبة من البرومبت"""
        files = []
        
        # استخراج الأسماء من البرومبت
        # مثل: "صنع صفحة login" -> login.py
        patterns = [
            r'(?:ملف|صفحة|class|function)\s+(\w+)',
            r'create\s+(\w+)',
            r'اكتب\s+(\w+)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, prompt, re.IGNORECASE)
            files.extend(matches)
        
        # إضافة الملفات الأساسية حسب اللغة
        if language == 'python':
            if intent == 'create':
                files.extend(['main.py', 'requirements.txt'])
        elif language == 'javascript':
            if intent == 'create':
                files.extend(['index.js', 'package.json'])
        elif language == 'html':
            files.extend(['index.html', 'style.css', 'script.js'])
        
        return list(set(files))[:10]  # 최대 10 ملفات
    
    def _generate_acceptance_criteria(self, prompt: str, intent: str) -> list:
        """إنشاء معايير القبول"""
        criteria = [
            "الكود خالٍ من أخطاء Syntax",
            "الكود قابل للتنفيذ",
        ]
        
        if intent == 'create':
            criteria.extend([
                "جميع الملفات المطلوبة تم إنشاؤها",
                "التبعيات محددة في ملف مناسب",
            ])
        elif intent == 'modify':
            criteria.extend([
                "التعديلات دقيقة ومحددة",
                "لا إعادة كتابة كاملة للملفات",
            ])
        
        return criteria
    
    def _get_build_commands(self, language: str, framework: str | None) -> list:
        """أوامر البناء"""
        commands = {
            'python': ['pip install -r requirements.txt'],
            'javascript': ['npm install'],
            'typescript': ['npm install && npm run build'],
            'go': ['go mod download'],
            'rust': ['cargo build --release'],
            'java': ['mvn compile'],
        }
        
        base = commands.get(language, ['echo "No build commands"'])
        
        if framework:
            if framework == 'django':
                base.append('python manage.py migrate')
            elif framework == 'react':
                base.append('npm run build')
        
        return base
    
    def _get_test_commands(self, language: str, framework: str | None) -> list:
        """أوامر الاختبار"""
        commands = {
            'python': ['pytest -v', 'python -m pytest --cov'],
            'javascript': ['npm test'],
            'typescript': ['npm test'],
            'go': ['go test -v ./...'],
            'rust': ['cargo test'],
            'java': ['mvn test'],
        }
        
        return commands.get(language, [])


def main():
    parser = argparse.ArgumentParser(description='محلل الطلبات - AI-1')
    parser.add_argument('--prompt', required=True, help='برومبت المستخدم')
    parser.add_argument('--request-id', help='معرف الطلب')
    parser.add_argument('--output', default='spec.json', help='ملف الإخراج')
    parser.add_argument('--model', default='chatgpt', choices=['chatgpt', 'gemini'], help='نموذج الذكاء الاصطناعي')
    
    args = parser.parse_args()
    
    # تحليل الطلب
    analyzer = RequestAnalyzer()
    spec = analyzer.analyze(args.prompt)
    
    # إضافة معرف الطلب
    if args.request_id:
        spec['request_id'] = args.request_id
    
    # إضافة معلومات النموذج
    spec['analysis_model'] = args.model
    
    # حفظ النتيجة
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(spec, f, ensure_ascii=False, indent=2)
    
    print(f"✅ تم إنشاء SPEC في: {output_path}")
    print(f"   النية: {spec['intent']}")
    print(f"   اللغة: {spec['language']}")
    print(f"   الملفات: {spec['files_needed']}")


if __name__ == '__main__':
    main()
