#!/usr/bin/env python3
import os
import glob
import csv
import zipfile

def build_csv_zip_report():
    print("[+] Initializing Ultra-Fast CSV/ZIP Matrix Engine...", flush=True)
    
    # 1. 마스터 타깃 목록 로드
    if not os.path.exists('targets.txt'):
        print("[-] Error: targets.txt missing.", flush=True)
        return
        
    with open('targets.txt', 'r') as f:
        targets = [line.strip() for line in f if line.strip()]

    # 완벽한 중복 제거 구조: { 도메인: { URL: set(도구들) } }
    matrix_data = {domain: {} for domain in targets}

    # 2. 12대 가상머신 데이터 전수조사
    txt_files = glob.glob('results/**/*.*', recursive=True) + glob.glob('results/*.*')
    txt_files = [f for f in txt_files if os.path.isfile(f)]

    if not txt_files:
        print("[-] Warning: No decrypted text files found in results/ folder.", flush=True)
        return

    print(f"[+] Processing {len(txt_files)} data source files...", flush=True)
    
    for file_path in txt_files:
        filename = os.path.basename(file_path).lower()
        if 'secretfinder' in filename: source_tool = 'SecretFinder'
        elif 'waybackurls' in filename: source_tool = 'Waybackurls'
        elif 'gau' in filename: source_tool = 'GAU'
        else: source_tool = 'Combined-Engine'

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    url = line.strip()
                    if not url or url.startswith('#'): continue
                    
                    for domain in targets:
                        if domain in url:
                            if url not in matrix_data[domain]:
                                matrix_data[domain][url] = set()
                            matrix_data[domain][url].add(source_tool)
                            break
        except Exception as e:
            print(f"[-] Error reading {filename}: {e}", flush=True)

    # 3. 임시 폴더 기틀 마련
    temp_dir = 'reports/csv_chunks'
    os.makedirs(temp_dir, exist_ok=True)
    generated_files = []

    # -----------------------------------------------------------------
    # [🔥대시보드 & 하이리스크 파일 선발 발급 가동]
    # -----------------------------------------------------------------
    dash_file = os.path.join(temp_dir, "00_Dashboard.csv")
    high_file = os.path.join(temp_dir, "01_High_Risk_Targets.csv")
    generated_files.extend([dash_file, high_file])

    f_dash = open(dash_file, 'w', encoding='utf-8-sig', newline='')
    f_high = open(high_file, 'w', encoding='utf-8-sig', newline='')

    writer_dash = csv.writer(f_dash)
    writer_high = csv.writer(f_high)

    # 대시보드 칼럼 요청 반영: No | 대상 도메인 | 총 URL 합계 | SecretFinder 탐지 건수
    writer_dash.writerow(["No", "Target Domain (대상 도메인)", "Total URLs (총 URL 합계)", "SecretFinder Count (SecretFinder 탐지 건수)"])
    writer_high.writerow(["No", "Domain (도메인)", "High Risk URL / Endpoint (위험 주소)", "Source Tool (탐지 도구)", "Risk Reason (위험 사유)"])

    high_risk_keywords = ['config', '.env', 'xml', 'json', 'secret', 'api/v', 'token', 'admin', 'password', 'key', 'credential', 'mysql']
    
    dash_idx = 1
    high_risk_idx = 1

    # 4. 개별 도메인 덤프 및 마스터 분석 연산
    print("[+] Compiling structural CSV assets and matrix dashboards...", flush=True)
    for domain, url_map in matrix_data.items():
        if not url_map: continue
        
        # [A] 대시보드 통계 기입 (중복 버블이 제거된 실존 고유 개수만 카운트)
        total_urls = len(url_map)
        secret_criticals = sum(1 for url, tools in url_map.items() if 'SecretFinder' in tools)
        writer_dash.writerow([dash_idx, domain, total_urls, secret_criticals])
        dash_idx += 1

        # [B] 개별 도메인 전용 단독 CSV 생성 파일 오픈
        domain_file_path = os.path.join(temp_dir, f"{domain}.csv")
        generated_files.append(domain_file_path)
        
        with open(domain_file_path, 'w', encoding='utf-8-sig', newline='') as f_dom:
            writer_dom = csv.writer(f_dom)
            writer_dom.writerow(["No", "Target URL / Endpoint (수집된 자산 주소)", "Source Tool (발견 도구)"])
            
            sorted_dataset = sorted(url_map.items(), key=lambda x: x[0])
            for idx, (url, tools) in enumerate(sorted_dataset, 1):
                tools_str = ", ".join(sorted(list(tools)))
                
                # 순수 도메인 파일 기입
                writer_dom.writerow([idx, url, tools_str])
                
                # [C] High Risk 자산 판별 및 기입
                is_high_risk = False
                reason = ""
                if 'SecretFinder' in tools:
                    is_high_risk = True
                    reason = "SecretFinder 소스코드 내 보안 자격증명 노출 의심"
                else:
                    url_lower = url.lower()
                    matched_keys = [key for key in high_risk_keywords if key in url_lower]
                    if matched_keys:
                        is_high_risk = True
                        reason = f"민감 엔드포인트 노출 파라미터 감지 ({', '.join(matched_keys)})"
                        
                if is_high_risk:
                    writer_high.writerow([high_risk_idx, domain, url, tools_str, reason])
                    high_risk_idx += 1

    # 마스터 스트림 안전 마감
    f_dash.close()
    f_high.close()

    # 5. 생성된 모든 CSV 자산을 단 하나의 마스터 ZIP 파일로 고압축 패킹
    final_zip_path = 'reports/passive_recon_report_v1.zip'
    print(f"[+] Bundling all assets into Master ZIP archive: {final_zip_path}", flush=True)
    
    with zipfile.ZipFile(final_zip_path, 'w', zipfile.ZIP_DEFLATED) as report_zip:
        for file in generated_files:
            if os.path.exists(file):
                report_zip.write(file, arcname=os.path.basename(file))
                os.remove(file) # 압축 완료된 원본 CSV 낱개 조각들은 즉시 삭제 청소

    try: os.rmdir(temp_dir)
    except: pass
    print("[+] [SUCCESS] Lightweight ZIP report engine execution complete!", flush=True)

if __name__ == '__main__':
    build_csv_zip_report()
