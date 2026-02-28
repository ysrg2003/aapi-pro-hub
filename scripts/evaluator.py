#!/usr/bin/env python3
"""
AAPI Pro Hub - المقيم/المراجع
يقارن النتائج مع SPEC ويحدد إذا كان هناك فشل
"""

import json
import argparse
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Tuple

class Evaluator:
    """المقيم - يقارن النتائج مع SPEC"""
    
    def __init__(self):
        self.max_iterations = 5
    
    def evaluate(self, spec: Dict, logs: str, exit_code: int, iteration: int) -> Dict[str, Any]:
        """
        تقييم النتيجة مقابل SPEC
        
        Returns:
            dict with:
                - passed: bool
                - failures: list of issues
                - recommendations: list of fixes
        """
        failures = []
        recommendations = []
        
        # 1. التحقق من exit code
        if exit_code != 0:
            failures.append({
                'type': 'execution_error',
                'severity': 'critical',
                'description': f'فشل التنفيذ بخروج رمز: {exit_code}',
                'logs': logs[:500],  # أول 500 حرف من السجلات
            })
            recommendations.append('فحص أخطاء الـ compilation')
        
        # 2. التحقق من معايير القبول
        for criterion in spec.get('acceptance_criteria', []):
            if not self._check_criterion(criterion, logs):
                failures.append({
                    'type': 'spec_mismatch',
                    'severity': 'high',
                    'description': f'لم يتحقق: {criterion}',
                })
                recommendations.append(f'تعديل الكود لتحقيق: {criterion}')
        
        # 3. التحقق من الملفات المطلوبة
        files_needed = spec.get('files_needed', [])
        for file_name in files_needed:
            if not self._check_file_exists(file_name, logs):
                failures.append({
                    'type': 'missing_file',
                    'severity': 'high',
                    'description': f'الملف الناقص: {file_name}',
                })
                recommendations.append(f'إنشاء الملف: {file_name}')
        
        # 4. تحديد القرار
        passed = len([f for f in failures if f['severity'] == 'critical']) == 0
        
        # 5. إذا فشلنا ولم نصل للحد الأقصى، اقترح إعادة المحاولة
        if not passed and iteration < self.max_iterations:
            recommendations.append(f'إعادة المحاولة (attempt {iteration + 1}/{self.max_iterations})')
        
        result = {
            'passed': passed,
            'iteration': iteration,
            'failures': failures,
            'recommendations': recommendations,
            'should_retry': not passed and iteration < self.max_iterations,
        }
        
        return result
    
    def _check_criterion(self, criterion: str, logs: str) -> bool:
        """التحقق من معيار واحد"""
        logs_lower = logs.lower()
        
        # كلمات تدل على الفشل
        failure_keywords = [
            'error', 'fail', 'exception', 'traceback',
            'syntax error', 'type error', 'reference error',
            'undefined', 'not found', 'cannot', 'لا يمكن'
        ]
        
        for keyword in failure_keywords:
            if keyword in logs_lower and criterion.lower() not in logs_lower:
                return False
        
        return True
    
    def _check_file_exists(self, file_name: str, logs: str) -> bool:
        """التحقق من وجود ملف"""
        # التحقق من السجلات
        return file_name in logs
    
    def generate_patch_instructions(self, failures: List[Dict], spec: Dict) -> List[Dict]:
        """
        إنشاء تعليمات_patch للتعديلات الدقيقة
        
        صيغة:
        - file: مسار الملف
        - operation: insert | replace | delete
        - after_line / start_line / end_line
        - content: المحتوى الجديد
        """
        patches = []
        
        for failure in failures:
            if failure['type'] == 'missing_file':
                # إنشاء ملف جديد
                patches.append({
                    'operation': 'create',
                    'file': failure.get('file', 'main.py'),
                    'content': f'# ملف جديد: {failure.get("description", "")}',
                    'reason': failure['description'],
                })
            
            elif failure['type'] == 'execution_error':
                # تحليل خطأ التنفيذ
                error_msg = failure.get('logs', '')
                patches.append({
                    'operation': 'analyze',
                    'error_message': error_msg,
                    'suggestion': 'فحص وتعديل الكود الذي يسبب الخطأ',
                })
        
        return patches
    
    def create_feedback_for_ai(self, result: Dict, spec: Dict) -> str:
        """إنشاء ملاحظات للذكاء الاصطناعي"""
        
        feedback = f"""
=== تقييم الطلب # iteration {result.get('iteration', 1)} ===

الحالة: {'✅ نجح' if result['passed'] else '❌ فشل'}

"""
        
        if result.get('failures'):
            feedback += "=== المشاكل ===\n"
            for i, failure in enumerate(result['failures'], 1):
                feedback += f"{i}. [{failure['severity']}] {failure['description']}\n"
        
        if result.get('recommendations'):
            feedback += "\n=== التوصيات ===\n"
            for rec in result['recommendations']:
                feedback += f"- {rec}\n"
        
        feedback += f"""
=== معلومات SPEC ===
- اللغة: {spec.get('language')}
- النية: {spec.get('intent')}
- الملفات المطلوبة: {spec.get('files_needed')}
"""
        
        return feedback


def run_tests(commands: List[str], cwd: str) -> Tuple[int, str]:
    """تشغيل أوامر الاختبار"""
    all_output = []
    
    for cmd in commands:
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=60
            )
            all_output.append(f"$ {cmd}\n{result.stdout}\n{result.stderr}")
            
            if result.returncode != 0:
                return result.returncode, '\n'.join(all_output)
        except subprocess.TimeoutExpired:
            return -1, f"Timeout: {cmd}"
        except Exception as e:
            return -1, str(e)
    
    return 0, '\n'.join(all_output)


def main():
    parser = argparse.ArgumentParser(description='المقيم - يقارن النتائج مع SPEC')
    parser.add_argument('--spec', required=True, help='ملف SPEC')
    parser.add_argument('--logs', required=True, help='مجلد السجلات')
    parser.add_argument('--iteration', default='1', help='رقم التكرار')
    parser.add_argument('--output', default='evaluation.json', help='ملف الإخراج')
    
    args = parser.parse_args()
    
    # تحميل SPEC
    with open(args.spec, 'r', encoding='utf-8') as f:
        spec = json.load(f)
    
    # تحميل السجلات
    logs_path = Path(args.logs)
    logs = ""
    if logs_path.exists():
        for log_file in logs_path.rglob('*.log'):
            with open(log_file, 'r', encoding='utf-8') as f:
                logs += f.read() + '\n'
    
    # تحديد exit code من السجلات
    exit_code = 0
    if 'error' in logs.lower() or 'fail' in logs.lower():
        exit_code = 1
    
    # التقييم
    evaluator = Evaluator()
    result = evaluator.evaluate(spec, logs, exit_code, int(args.iteration))
    
    # إنشاء تعليمات_patch
    if not result['passed']:
        patches = evaluator.generate_patch_instructions(result['failures'], spec)
        result['patches'] = patches
        
        # إنشاء ملاحظات للذكاء الاصطناعي
        result['ai_feedback'] = evaluator.create_feedback_for_ai(result, spec)
    
    # حفظ النتيجة
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    # طباعة النتيجة
    if result['passed']:
        print("✅ نجح الطلب!")
    else:
        print(f"❌ فشل (attempt {args.iteration})")
        for rec in result.get('recommendations', []):
            print(f"   → {rec}")
    
    print(f"\n📄 saved to: {output_path}")


if __name__ == '__main__':
    main()
