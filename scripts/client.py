#!/usr/bin/env python3
"""
AAPI Pro Hub - Python SDK
مكتبة العميل للتواصل مع النظام
"""

import requests
import time
import json
import uuid
import zipfile
import io
from typing import Optional, Dict, Any

class AAPIProClient:
    """
    العميل للاتصال بـ AAPI Pro Hub
    """
    
    def __init__(self, token: str, owner: str, repo: str):
        """
        تهيئة العميل
        
        Args:
            token: GitHub Personal Access Token
            owner: اسم المستخدم/المنظمة
            repo: اسم المستودع
        """
        self.token = token
        self.owner = owner
        self.repo = repo
        self.base_url = f"https://api.github.com/repos/{owner}/{repo}"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def ask_ai(
        self, 
        prompt: str, 
        engine: str = "gemini",
        timeout: int = 300,
        poll_interval: int = 5
    ) -> Dict[str, Any]:
        """
        إرسال سؤال للذكاء الاصطناعي والحصول على الرد
        
        Args:
            prompt: السؤال/البرومبت
            engine: المحرك (gemini, chatgpt, auto)
            timeout: timeout بالثواني
            poll_interval:فترة الفحص بالثواني
        
        Returns:
            dict with response and metadata
        """
        workflow = self._get_workflow(engine)
        request_id = self._generate_request_id()
        
        print(f"📡 إرسال الطلب لـ {engine}...")
        print(f"   Request ID: {request_id}")
        
        # 1. إرسال الطلب
        trigger_url = f"{self.base_url}/actions/workflows/{workflow}/dispatches"
        data = {
            "ref": "main",
            "inputs": {
                "prompt": prompt,
                "request_id": request_id
            }
        }
        
        res = requests.post(trigger_url, headers=self.headers, json=data)
        
        if res.status_code != 204:
            return {
                "success": False,
                "error": f"HTTP {res.status_code}: {res.text}"
            }
        
        # 2. انتظار النتائج
        print(f"⏳ جاري المعالجة سحابياً... (قد تستغرق 30-60 ثانية)")
        
        artifact_name = f"{engine}-json-{request_id}"
        result_file = f"{engine}_result.json"
        
        start_time = time.time()
        attempts = timeout // poll_interval
        
        for attempt in range(attempts):
            time.sleep(poll_interval)
            
            # فحص التشغيلات المكتملة
            runs_url = f"{self.base_url}/actions/runs?status=completed&per_page=10"
            run_data = requests.get(runs_url, headers=self.headers).json()
            
            for run in run_data.get("workflow_runs", []):
                # جلب Artifacts
                arts_res = requests.get(run["artifacts_url"], headers=self.headers).json()
                
                for art in arts_res.get("artifacts", []):
                    if art["name"] == artifact_name:
                        print("📥 تم استلام الرد! جاري التحميل...")
                        
                        # تحميل الـ artifact
                        zip_res = requests.get(art["archive_download_url"], headers=self.headers)
                        
                        try:
                            with zipfile.ZipFile(io.BytesIO(zip_res.content)) as z:
                                if result_file in z.namelist():
                                    with z.open(result_file) as f:
                                        result = json.loads(f.read().decode('utf-8'))
                                        return {
                                            "success": True,
                                            "response": result.get("response", ""),
                                            "request_id": request_id,
                                            "model": engine,
                                            "data": result
                                        }
                        except zipfile.BadZipFile:
                            # ربما الملف ليس مضغوطاً
                            pass
        
        return {
            "success": False,
            "error": "Timeout: استغرق الوقت أطول من المتوقع"
        }
    
    def ask_with_full_pipeline(
        self,
        prompt: str,
        max_iterations: int = 5,
        verbose: bool = True
    ) -> Dict[str, Any]:
        """
        تشغيل خط الإنتاج الكامل (تحليل + توليد + تنفيذ + تقييم)
        
        Args:
            prompt: البرومبت
            max_iterations: الحد الأقصى للتكرارات
            verbose: طباعة التفاصيل
        
        Returns:
            dict with final result
        """
        iteration = 1
        current_prompt = prompt
        
        while iteration <= max_iterations:
            if verbose:
                print(f"\n{'='*50}")
                print(f"📌 المحاولة {iteration}/{max_iterations}")
                print(f"{'='*50}")
            
            # تشغيل الطلب
            result = self.ask_ai(current_prompt, engine="auto")
            
            if not result["success"]:
                return {
                    "success": False,
                    "error": result["error"],
                    "iterations": iteration
                }
            
            # في النظام الكامل، هنا يتم التحقق من التنفيذ
            # للتوضيح، نفترض نجاح المحاولة الأولى
            if verbose:
                print(f"\n✅ نجح الطلب!")
            
            return {
                "success": True,
                "response": result["response"],
                "iterations": iteration,
                "request_id": result.get("request_id")
            }
        
        return {
            "success": False,
            "error": " reached_max_iterations",
            "iterations": max_iterations
        }
    
    def check_workflow_status(self, run_id: int) -> Dict[str, Any]:
        """فحص حالة سير عمل معين"""
        url = f"{self.base_url}/actions/runs/{run_id}"
        res = requests.get(url, headers=self.headers)
        
        if res.status_code == 200:
            return res.json()
        return {"error": f"HTTP {res.status_code}"}
    
    def list_workflows(self) -> list:
        """عرض سير العمل المتاحة"""
        url = f"{self.base_url}/actions/workflows"
        res = requests.get(url, headers=self.headers)
        
        if res.status_code == 200:
            return res.json().get("workflows", [])
        return []
    
    def _get_workflow(self, engine: str) -> str:
        """الحصول على اسم ملف سير العمل"""
        workflows = {
            "gemini": "gemini_api.yml",
            "chatgpt": "gpt_api.yml",
            "auto": "main.yml"
        }
        return workflows.get(engine, "main.yml")
    
    def _generate_request_id(self) -> str:
        """توليد معرف فريد"""
        return str(uuid.uuid4().hex)[:12]


# ============ مثال الاستخدام ============

def main():
    """مثال على استخدام المكتبة"""
    
    # تهيئة العميل
    client = AAPIProClient(
        token="ghp_xxxxxxxxxxxx",
        owner="username",
        repo="aapi-pro-hub"
    )
    
    # الطريقة 1: سؤال مباشر
    print("=== الطريقة 1: سؤال مباشر ===")
    result = client.ask_ai(
        prompt="اكتب لي دالة بايثون لحساب Factorial",
        engine="gemini"
    )
    
    if result["success"]:
        print(f"✅ الرد: {result['response'][:200]}...")
    else:
        print(f"❌ خطأ: {result['error']}")
    
    # الطريقة 2: خط الإنتاج الكامل
    print("\n=== الطريقة 2: خط الإنتاج الكامل ===")
    result2 = client.ask_with_full_pipeline(
        prompt="أنشئ لي صفحة HTML لمعرض صور",
        max_iterations=3
    )
    
    if result2["success"]:
        print(f"✅ تم بنجاح في {result2['iterations']} محاولات!")
    else:
        print(f"❌ فشل: {result2['error']}")


if __name__ == "__main__":
    main()
