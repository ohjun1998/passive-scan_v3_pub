#!/usr/bin/env python3
import os
import glob
import requests

def upload_report_safe_engine():
    webhook_url = os.environ.get('DISCORD_WEBHOOK_URL')
    if not webhook_url:
        print("[-] Error: DISCORD_WEBHOOK_URL variable is missing.")
        return

    # 최신 생성된 마스터 ZIP 리포트 탐색
    files = glob.glob('reports/passive_recon_report_v*.zip')
    if not files:
        print("[-] Error: No ZIP report asset found in reports/ folder.")
        return
    
    latest_zip = max(files, key=os.path.getmtime)
    zip_name = os.path.basename(latest_zip)
    
    print(f"[+] Transmitting clean compressed master archive to Discord: {zip_name}", flush=True)
    with open(latest_zip, 'rb') as f:
        payload = {
            'content': (
                f"🚀 **[정찰 완료 - 초경량 CSV-ZIP 마스터 보고서]**\n"
                f"🔒 65개 대상 자산 결과가 중복 제거 및 도구 병합 처리를 거쳐 압축 발송되었습니다.\n\n"
                f"💡 **참고사항:**\n"
                f"압축 파일 내부의 `00_Dashboard.csv`와 `01_High_Risk_Targets.csv`를 통해 종합 통계를 먼저 확인하신 뒤, 각 도메인별 개별 CSV 파일을 조회하세요!"
            )
        }
        files_payload = {'file': (zip_name, f, 'application/zip')}
        response = requests.post(webhook_url, data=payload, files=files_payload)
        
    if response.status_code in [200, 204]:
        print("[+] [SUCCESS] Native single-packet Discord transmission complete!", flush=True)
    else:
        print(f"[-] Discord error code: {response.status_code}, {response.text}", flush=True)

if __name__ == '__main__':
    upload_report_safe_engine()
