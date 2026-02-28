#!/usr/bin/env python3
"""
AAPI Pro Hub - المُعدِّل الذكي (Patcher)
يُجري تعديلات دقيقة على الملفات بدون إعادة كتابة كاملة

صيغة التعديلات المدعومة:
- INSERT after_line N: content
- REPLACE lines N-M: content  
- DELETE lines N-M
- APPEND: content
"""

import json
import argparse
import re
from pathlib import Path
from typing import Dict, List, Any, Optional

class SmartPatcher:
    """المُعدِّل الذكي - يُجري تعديلات دقيقة"""
    
    def __init__(self):
        pass
    
    def apply_patch(self, file_path: str, patch: Dict[str, Any]) -> bool:
        """
        تطبيق patch واحد على ملف
        
        Args:
            file_path: مسار الملف
            patch: dict with operation, after_line, content, etc.
        
        Returns:
            bool: نجاح العملية
        """
        try:
            path = Path(file_path)
            if not path.exists():
                print(f"  ⚠️ الملف غير موجود: {file_path}")
                return False
            
            # قراءة الملف
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            operation = patch.get('operation', 'insert')
            content = patch.get('content', '')
            
            if operation == 'insert':
                # إدراج بعد سطر معين
                after_line = patch.get('after_line', 0)
                new_lines = content.split('\n')
                
                # إضافة سطر جديد بعد السطر المحدد
                insert_index = min(after_line, len(lines))
                for i, new_line in enumerate(new_lines):
                    lines.insert(insert_index + i, new_line + '\n')
            
            elif operation == 'replace':
                # استبدال نطاق من الأسطر
                start_line = patch.get('start_line', 0)
                end_line = patch.get('end_line', len(lines))
                new_lines = content.split('\n')
                
                # التأكد من صحة النطاق
                start_index = max(0, start_line - 1)  # التحويل من 1-based
                end_index = min(len(lines), end_line)
                
                # الاستبدال
                lines = lines[:start_index] + [l + '\n' for l in new_lines if l] + lines[end_index:]
            
            elif operation == 'delete':
                # حذف نطاق من الأسطر
                start_line = patch.get('start_line', 0)
                end_line = patch.get('end_line', len(lines))
                
                start_index = max(0, start_line - 1)
                end_index = min(len(lines), end_line)
                
                lines = lines[:start_index] + lines[end_index:]
            
            elif operation == 'append':
                # إضافة في نهاية الملف
                lines.append('\n' + content)
            
            # كتابة الملف
            with open(path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            return True
            
        except Exception as e:
            print(f"  ❌ خطأ في التطبيق: {e}")
            return False
    
    def apply_patches(self, patches: List[Dict[str, Any]], base_dir: str = '.') -> Dict[str, bool]:
        """
        تطبيق مجموعة من الـ patches
        
        Args:
            patches: قائمة من الـ patches
            base_dir: المجلد الأساسي
        
        Returns:
            dict: نتيجة كل patch
        """
        results = {}
        
        for i, patch in enumerate(patches):
            file_path = patch.get('file', 'main.py')
            full_path = Path(base_dir) / file_path
            
            print(f"  [{i+1}] Applying to {file_path}...")
            
            if patch.get('operation') == 'create':
                # إنشاء ملف جديد
                full_path.parent.mkdir(parents=True, exist_ok=True)
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(patch.get('content', ''))
                results[file_path] = True
                print(f"     ✓ Created: {file_path}")
            
            elif patch.get('operation') == 'analyze':
                # تحليل فقط - لا تغيير
                print(f"     ℹ️ Analysis: {patch.get('suggestion', '')}")
                results[file_path] = True
            
            else:
                # تطبيق تعديل
                success = self.apply_patch(str(full_path), patch)
                results[file_path] = success
                if success:
                    print(f"     ✓ Modified: {file_path}")
        
        return results
    
    def generate_patch_from_diff(self, old_content: str, new_content: str, file_path: str) -> Dict[str, Any]:
        """
        توليد patch من مقارنة محتوى قديم وجديد
        
        This is a simplified version - in production, use proper diff
        """
        old_lines = old_content.split('\n')
        new_lines = new_content.split('\n')
        
        # إيجاد الاختلافات
        patch = {
            'file': file_path,
            'operation': 'replace',
            'changes_detected': True,
        }
        
        if len(new_lines) > len(old_lines):
            # إضافة أسطر
            patch['operation'] = 'insert'
            patch['after_line'] = len(old_lines)
            patch['added_lines'] = new_lines[len(old_lines):]
        
        return patch
    
    def parse_patch_instructions(self, instructions: str) -> List[Dict[str, Any]]:
        """
        تحليل تعليمات_patch من نص
        
        Examples:
            - "AFTER line 10: print('hello')"
            - "REPLACE lines 5-10 with: ..."
            - "DELETE lines 15-20"
            - "INSERT at line 5: ..."
        """
        patches = []
        
        lines = instructions.split('\n')
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # أنماط مختلفة
            patterns = [
                (r'AFTER\s+line\s+(\d+):\s*(.+)', 'insert'),
                (r'REPLACE\s+lines\s+(\d+)-(\d+)\s+with:\s*(.+)', 'replace'),
                (r'DELETE\s+lines\s+(\d+)-(\d+)', 'delete'),
                (r'INSERT\s+at\s+line\s+(\d+):\s*(.+)', 'insert'),
            ]
            
            for pattern, operation in patterns:
                match = re.match(pattern, line, re.IGNORECASE)
                if match:
                    patch = {'operation': operation}
                    
                    if operation == 'insert':
                        patch['after_line'] = int(match.group(1))
                        patch['content'] = match.group(2)
                    elif operation == 'replace':
                        patch['start_line'] = int(match.group(1))
                        patch['end_line'] = int(match.group(2))
                        patch['content'] = match.group(3)
                    elif operation == 'delete':
                        patch['start_line'] = int(match.group(1))
                        patch['end_line'] = int(match.group(2))
                    
                    patches.append(patch)
                    break
        
        return patches
    
    def create_patch_file(self, patches: List[Dict], output_path: str):
        """إنشاء ملف patch"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(patches, f, ensure_ascii=False, indent=2)
        print(f"✅ Created patch file: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='المُعدِّل الذكي - يُجري تعديلات دقيقة')
    parser.add_argument('--patches', required=True, help='ملف الـ patches (JSON)')
    parser.add_argument('--directory', default='.', help='مجلد العمل')
    parser.add_argument('--output', help='ملف النتيجة (اختياري)')
    
    args = parser.parse_args()
    
    # تحميل patches
    with open(args.patches, 'r', encoding='utf-8') as f:
        patches = json.load(f)
    
    if isinstance(patches, dict) and 'patches' in patches:
        patches = patches['patches']
    
    # تطبيق
    patcher = SmartPatcher()
    results = patcher.apply_patches(patches, args.directory)
    
    # ملخص
    success_count = sum(1 for v in results.values() if v)
    total_count = len(results)
    
    print(f"\n=== ملخص التعديلات ===")
    print(f"  ✓ نجحت: {success_count}/{total_count}")
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump({
                'results': results,
                'summary': {
                    'total': total_count,
                    'successful': success_count,
                    'failed': total_count - success_count
                }
            }, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    main()
