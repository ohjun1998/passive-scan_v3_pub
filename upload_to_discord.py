#!/usr/bin/env python3
import os
import glob
import requests

def upload_latest_report_to_discord():
    # GitHub Secrets에서 안전하게 전달받은 웹훅 주소 매핑
    webhook_url = os.environ.get('DISCORD_WEBHOOK_URL')

    if not webhook_url:
        print("[-] Error: DISCORD_WEBHOOK_URL environment variable is missing.")
        return

    # reports/ 폴더 내에서 생성된 엑셀 마스터 보고서 목록 탐색
    files = glob.glob('reports/passive_recon_report_v*.xlsx')
    if not files:
        print("[-] Error: No excel report found in reports/ folder.")
        return
    
    # 가장 최근에 수정/생성된 최신 버전 파일 선택
    latest_file = max(files, key=os.path.getmtime)
    file_name = os.path.basename(latest_file)

    print(f"[+] Found latest report: {file_name} ({os.path.getsize(latest_file) / 1024 / 1024:.2f} MB)")
    print(f"[+] Exfiltrating report to Private Discord Channel...")

    # 디스코드 파일 첨부 규격(Multipart)에 맞춰 바이너리 스트림 전송
    with open(latest_file, 'rb') as f:
        payload = {
            'content': f"🚀 **[정찰 완료]** 3중 초병렬 분산 스캔 마스터 보고서가 배달되었습니다.\n📅 파일명: `{file_name}`"
        }
        files_payload = {
            'file': (file_name, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        }
        
        response = requests.post(webhook_url, data=payload, files=files_payload)

    # 디스코드 웹훅의 정상 전송 반환값(200 OK 또는 204 No Content) 검증
    if response.status_code in [200, 204]:
        print(f"[+] [SUCCESS] File transmission to Discord complete! Check your mobile app notification.")
    else:
        print(f"[-] Error: Failed to send file. Status code: {response.status_code}, Response: {response.text}")

if __name__ == '__main__':
    upload_latest_report_to_discord()
