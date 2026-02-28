# AAPI Pro Hub - المواصفات التقنية

## 1. نظرة عامة على النظام

**الهدف:** بناء نظام أتمتة برمجية يستخدم GitHub Actions كـ backend لتحويل طلبات المستخدمين إلى مشاريع برمجية كاملة.

## 2. دورة التنفيذ

### 2.1 الخطوات الأساسية

1. **استلام البرومبت** ← من صفحة الويب
2. **AI-1 (المحلل)** ← يفهم الطلب ويُنشئ SPEC مُنظَّم
3. **تجميد SPEC** ← قفل المواصفات للمرحلة التالية
4. **AI-2 (المُنتج)** ← يحول SPEC لكود برمجي
5. **دفع للكود** ← رفع للـ branch
6. **GitHub Actions** ← Install, Build, Test, Lint
7. **تجميع النتائج** ← Logs, Exit codes, Coverage
8. **المُقيِّم** ← مقارنة النتائج مقابل SPEC
9. **إذا فشل:** ← تعليمات_patch ← AI-1 ← AI-2 ← كرر
10. **إذا نجح:** ← Merge

### 2.2 التنفيذ الدقيق (STRICT EXECUTION CONTRACT)

#### قواعد التعديل:
- ❌ لا تُعِد كتابة الملف من الأول
- ✅ استخدمPATCH instructions محددة:
  - `AFTER line X: insert Y`
  - `REPLACE lines X-Y with Z`
  - `DELETE lines X-Y`
  - `INSERT at line X: Y`

## 3. هيكل GitHub Actions

### 3.1 main.yml - سير العمل الرئيسي

```yaml
name: AAPI Pro Main Pipeline
on:
  workflow_dispatch:
    inputs:
      prompt:
        description: 'برومبت المستخدم'
        required: true
      request_id:
        description: 'معرف الطلب الفريد'
        required: true
      spec:
        description: 'مواصفات SPEC (اختياري)'
        required: false
      iteration:
        description: 'رقم التكرار'
        required: false
        default: '1'
```

### 3.2 gemini_api.yml - دمج Gemini

```yaml
name: Gemini API Integration
on:
  workflow_dispatch:
    inputs:
      prompt:
        required: true
      request_id:
        required: true
```

### 3.3 gpt_api.yml - دمج ChatGPT

```yaml
name: ChatGPT API Integration
on:
  workflow_dispatch:
    inputs:
      prompt:
        required: true
      request_id:
        required: true
```

## 4.剧本 Scripts Python

### 4.1 analyzer.py - محلل الطلبات

**المدخلات:**
- `prompt`: برومبت المستخدم

**المخرجات:**
```json
{
  "intent": "create|modify|analyze|...",
  "language": "python|javascript|...",
  "framework": "django|react|...",
  "files_needed": ["main.py", "utils.py"],
  "acceptance_criteria": [
    "الكود يشتغل بدون أخطاء",
    "يدعم X و Y"
  ],
  "detailed_spec": "..."
}
```

### 4.2 code_generator.py - مولد الكود

**المدخلات:**
- `spec`: مواصفات مُنظَّمة من analyzer
- `mode`: create | patch
- `existing_files`: ملفات حالية (للوضع patch)

**المخرجات:**
```json
{
  "files_created": ["file1.py"],
  "files_modified": ["file2.py"],
  "patches": [
    {
      "file": "file2.py",
      "action": "replace",
      "start_line": 10,
      "end_line": 15,
      "content": "..."
    }
  ],
  "test_commands": ["pytest tests/", "npm test"],
  "build_commands": ["pip install -r requirements.txt"]
}
```

### 4.3 evaluator.py - المقيم

**المدخلات:**
- `spec`: المواصفات الأصلية
- `execution_results`: نتائج التنفيذ
- `logs`: سجلات الأخطاء

**المخرجات:**
```json
{
  "passed": true|false,
  "failures": [
    {
      "type": "execution_error|test_failure|spec_mismatch",
      "location": "file:line",
      "description": "...",
      "suggestion": "..."
    }
  ],
  "coverage_percentage": 85,
  "recommendations": ["...", "..."]
}
```

### 4.4 patcher.py - المُعدِّل الذكي

**المدخلات:**
- `files`: الملفات المطلوب تعديلها
- `patches`: قائمة التعديلات

**قواعد التعديل:**
```python
# مثال على صيغة التعديل
patch = {
    "file": "src/main.py",
    "operation": "replace",  # insert | replace | delete
    "after_line": 15,
    "content": "new_content_here"
}
```

## 5. واجهة المستخدم (index.html)

### 5.1 الحقول المطلوبة
- GitHub Token (يُحفظ محلياً)
- المستودع (格式: username/repo)
- محرر النصوص للـ prompt
- اختيار المحرك (Gemini/ChatGPT)

### 5.2 الوظائف
- إرسال الطلب عبر GitHub API
- تتبع حالة التنفيذ
- جلب النتائج من Artifacts
- عرض الأخطاء والمخرجات

## 6. معايير الجودة

### 6.1 STRICT EXECUTION CONTRACT

1. **فصل الأدوار:**
   - ChatGPT-5: التحليل + التوليد الرئيسي
   - Gemini 3 Flash: المراجعة + تحسينات السياق الطويل

2. **قواعد التكرار:**
   - الحد الأقصى: 5 تكرارات
   - وقت التنفيذ لكل محاولة: 5 دقائق
   - timeout: 2.5 دقيقة

3. **التعديلات:**
   - استخدام diff/patch فقط
   - تحديد الأسطر تحديداً
   - لا إعادة كتابة كاملة

### 6.2 GitHub Features

- **Releases:** إصدار تلقائي عند النجاح
- **Caches:** تخزين مؤقت للتبعيات
- **Artifacts:** تخزين النتائج intermedia

## 7. ضغط الملفات

### 7.1 استخدام Zstd

```bash
# ضغط
tar -I zstd -cvf output.tar.zst files/

# فك الضغط
tar -I zstd -xvf output.tar.zst
```

### 7.2 في GitHub Actions

```yaml
- name: Compress output
  run: tar -I zstd -cvf results.tar.zst output/

- name: Upload Artifact
  uses: actions/upload-artifact@v4
  with:
    name: results-${{ github.run_id }}
    path: results.tar.zst
```

## 8.，环境 المتغيرات

| المتغير | الوصف |
|---------|-------|
| `GEMINI_API_KEY` | مفتاح Gemini API |
| `OPENAI_API_KEY` | مفتاح OpenAI API |
| `GITHUB_TOKEN` | Token للوصول |

## 9. جدول القرارات

| السيناريو | الإجراء |
|----------|---------|
| فشل compilation | كرر مع تصحيح الأخطاء |
| فشل tests | كرر مع إصلاح الـ tests |
| عدم تطابق مع SPEC | كرر مع تعديل الكود |
| timeout | كرر من آخر نقطة نجاح |
| نجاح | إنشاء release + دمج |

## 10. ملاحظات الأمان

- ✅ Token يُحفظ محلياً (localStorage)
- ✅ لا يُرفع للـ repo
- ✅ استخدام HTTPS دائماً
- ✅ صلاحيات محددة للـ token
