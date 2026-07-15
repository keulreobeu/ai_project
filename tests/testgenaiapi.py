import os
import sys

try:
    from google import genai
except ImportError:
    print("❌ [오류] google-genai 패키지가 설치되지 않았습니다. 'pip install google-genai'를 실행하세요.")
    sys.exit(1)

def test_connection():
    # 1. API 키 환경 변수 확인
    api_key = "AIzaSyDVm34QHNr5YKX1pfjzIC2UZfdtc6x5z_A" # os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ [오류] GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")
        print("터미널에 환경 변수를 설정하거나 코드의 Client(api_key='...')에 직접 입력하세요.")
        return

    print("🔍 API Key 감지 성공 (앞 4자리):", api_key[:4] + "****")
    print("🔄 Gemini Client 초기화 중...")
    
    try:
        # 2. 클라이언트 초기화 (자동으로 GEMINI_API_KEY 환경 변수를 읽어옴)
        client = genai.Client(api_key=api_key)

        print("⚡ API 호출 시도 중...")
        # 3. 아주 단순한 텍스트 생성 테스트 (gemini-2.5-flash 사용)
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents="Hello! If you can hear me, please reply with 'Connection Successful!'",
        )
        
        # 4. 결과 출력
        print("\n================ Gemini Response ================")
        print(response.text)
        print("=================================================")
        print("\n🎉 [성공] Gemini API 연결 및 텍스트 생성 테스트 완료!")

    except Exception as e:
        print(f"\n❌ [API 오류 발생]: {e}")
        print("API 키가 올바른지 혹은 네트워크 상태(VPN 등)를 확인해 주세요.")

if __name__ == "__main__":
    test_connection()