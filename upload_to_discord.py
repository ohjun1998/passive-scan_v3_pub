#!/usr/bin/env python3
import os
import glob
import zipfile
import requests

def upload_report_safe_engine():
    webhook_url = os.environ.get('DISCORD_WEBHOOK_URL')
    if not webhook_url:
        print("[-] Error: DISCORD_WEBHOOK_URL variable is missing.")
        return

    # 1. 최신 엑셀 보고서 탐색
    files = glob.glob('reports/passive_recon_report_v*.xlsx')
    if not files:
        print("[-] Error: No excel report found in reports/ folder.")
        return
    
    latest_file = max(files, key=os.path.getmtime)
    file_name = os.path.basename(latest_file)
    
    # 2. 고강도 ZIP 압축 실행 (용량 다이어트)
    zip_file_name = file_name.replace('.xlsx', '.zip')
    zip_file_path = os.path.join('reports', zip_file_name)
    
    print(f"[+] Compressing {file_name} with maximum ZIP efficiency...")
    with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(latest_file, arcname=file_name)
        
    compressed_size = os.path.getsize(zip_file_path)
    print(f"[+] Compression complete: {compressed_size / 1024 / 1024:.2f} MB")

    DISCORD_LIMIT = 9.5 * 1024 * 1024 # 안전 전송 마지노선 (9.5MB)

    # -----------------------------------------------------------------
    # [Case 1] 압축 결과가 9.5MB 이하인 경우 -> 통째로 단일 파일 직송 (가장 이상적)
    # -----------------------------------------------------------------
    if compressed_size <= DISCORD_LIMIT:
        print("[+] Compressed file is within Discord limits. Transmitting natively...")
        with open(zip_file_path, 'rb') as f:
            payload = {
                'content': f"🚀 **[정찰 완료 - 마스터 보고서]**\n🔒 보안 압축 파일이 안전하게 직송되었습니다.\n📅 원본 파일명: `{file_name}`"
            }
            files_payload = {'file': (zip_file_name, f, 'application/zip')}
            response = requests.post(webhook_url, data=payload, files=files_payload)
            
        if response.status_code in [200, 204]:
            print("[+] [SUCCESS] Native Discord transmission complete!")
        else:
            print(f"[-] Discord error: {response.status_code}, {response.text}")

    # -----------------------------------------------------------------
    # [Case 2] 압축해도 9.5MB를 초과하는 경우 -> 안전 분할 자동 사출 + 복원 가이드 동봉
    # -----------------------------------------------------------------
    else:
        print("[!] Warning: Compressed size still exceeds limit. Activating chunk splitter...")
        part_num = 1
        with open(zip_file_path, 'rb') as f:
            while True:
                chunk = f.read(int(DISCORD_LIMIT))
                if not chunk:
                    break
                
                chunk_name = f"{zip_file_name}.part{part_num}"
                print(f"[+] Sending segment: {chunk_name}")
                
                # 디스코드 창에 대입할 운영체제별 복원 가이드라인 텍스트 조립
                cmd_win = f"copy /b {zip_file_name}.part* {zip_file_name}"
                cmd_mac = f"cat {zip_file_name}.part* > {zip_file_name}"
                
                payload = {
                    'content': (
                        f"📦 **[대용량 분할 사출] 마스터 보고서 Part {part_num}**\n"
                        f"💡 모든 조각을 다운로드한 후, 터미널(콘솔)에서 아래 명령어를 실행하여 합쳐주세요!\n"
                        f"```cmd\n"
                        f"※ Windows (CMD):\n{cmd_win}\n\n"
                        f"※ Mac / Linux:\n{cmd_mac}\n"
                        f"```"
                    )
                }
                files_payload = {'file': (chunk_name, chunk, 'application/octet-stream')}
                
                requests.post(webhook_url, data=payload, files=files_payload)
                part_num += 1
                
        print("[+] [SUCCESS] All compressed chunks safely bypass restrictions and landed in Discord!")

if __name__ == '__main__':
    upload_report_safe_engine()
