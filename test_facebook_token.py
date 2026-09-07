#!/usr/bin/env python3
# test_facebook_token.py
# اختبار آمن لصلاحية Facebook Page Access Token
# لا تطبع التوكن. احفظه في متغير بيئة FACEBOOK_PAGE_ACCESS_TOKEN أو مرره كوسيط.

import os
import sys
import argparse
import requests
import json

GRAPH_API_BASE = "https://graph.facebook.com/v17.0"
PAGE_ID_KNOWN = "1183775391493528"  # Page ID الذي ذكرتَه

def safe_print_json(obj):
    # نحذف أي مفاتيح access_token من المخرجات قبل الطباعة
    def remove_tokens(o):
        if isinstance(o, dict):
            return {k: remove_tokens(v) for k, v in o.items() if k != "access_token"}
        if isinstance(o, list):
            return [remove_tokens(i) for i in o]
        return o
    cleaned = remove_tokens(obj)
    print(json.dumps(cleaned, ensure_ascii=False, indent=2))

def call_graph(path, params):
    url = f"{GRAPH_API_BASE}{path}"
    try:
        r = requests.get(url, params=params, timeout=20)
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}
    try:
        data = r.json()
    except Exception:
        return {"error": f"Non-JSON response, status {r.status_code}", "text": r.text}
    if r.status_code >= 400:
        return {"http_status": r.status_code, "error": data}
    return data

def main():
    parser = argparse.ArgumentParser(description="Test Facebook Page Access Token (safe).")
    parser.add_argument("--token", help="Page Access Token (optional). Prefer using env var FACEBOOK_PAGE_ACCESS_TOKEN.")
    args = parser.parse_args()

    token = args.token or os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN")
    if not token:
        print("خطأ: لم أجد توكن. عيّنه في متغير البيئة FACEBOOK_PAGE_ACCESS_TOKEN أو مرره عبر --token")
        sys.exit(1)

    params = {"access_token": token}

    print("\n1) استدعاء /me/accounts — هل تظهر صفحتك هنا؟")
    res_accounts = call_graph("/me/accounts", params)
    safe_print_json(res_accounts)

    print("\n2) استدعاء /{PAGE_ID}?fields=id,name — تحقق من بيانات الصفحة (قراءة فقط).")
    res_page = call_graph(f"/{PAGE_ID_KNOWN}", {"fields": "id,name", "access_token": token})
    safe_print_json(res_page)

    print("\n3) استدعاء /me/permissions — الأذونات الممنوحة لهذا التوكن.")
    res_perms = call_graph("/me/permissions", params)
    safe_print_json(res_perms)

    print("\n4) استدعاء /{PAGE_ID}/feed?limit=1 — اختبار قراءة آخر منشور (قراءة فقط).")
    res_feed = call_graph(f"/{PAGE_ID_KNOWN}/feed", {"limit": "1", "access_token": token})
    safe_print_json(res_feed)

    # موجز سريع محلي
    print("\n--- موجز النتائج المطلوب إرساله لي (لا ترسل التوكن) ---")
    # هل الصفحة ظهرت في /me/accounts؟
    page_found = False
    try:
        accounts = res_accounts.get("data", [])
        for p in accounts:
            if str(p.get("id")) == PAGE_ID_KNOWN:
                page_found = True
                break
    except Exception:
        page_found = False
    print(f"- Page present in /me/accounts: {'نعم' if page_found else 'لا'}")
    # هل استدعاء بيانات الصفحة نجح؟
    page_ok = "error" not in res_page and res_page.get("id") == PAGE_ID_KNOWN
    print(f"- /{PAGE_ID_KNOWN} returned id/name: {'نعم' if page_ok else 'لا'}")
    # الأذونات الموجودة
    perms_list = []
    try:
        for item in res_perms.get("data", []):
            if item.get("status") == "granted":
                perms_list.append(item.get("permission"))
    except Exception:
        perms_list = []
    print(f"- Granted permissions (sample): {perms_list}")
    # هل قراءة الـ feed نجحت؟
    feed_ok = "error" not in res_feed
    print(f"- Read feed success: {'نعم' if feed_ok else 'لا'}")

    print("\nأرسل لي النص الكامل للمخرجات أعلاه (JSON أو رسائل الخطأ) حتى أتابع الخطوات التالية.")

if __name__ == "__main__":
    main()
