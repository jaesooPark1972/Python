#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🛡️ 크래시 방지 시스템
===================
프로그램 에러 발생 시 자동 로깅 및 사용자 알림

Author: Park Jae-soo (SKY Group)
Version: 1.0
"""

import sys
import traceback
import os
from datetime import datetime
from tkinter import messagebox

class CrashHandler:
    """
    프로그램 크래시 방지 및 에러 로깅 시스템
    """
    
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        # 에러 핸들러 등록
        sys.excepthook = self.handle_exception
        
    def handle_exception(self, exc_type, exc_value, exc_traceback):
        """
        예외 발생 시 자동 처리
        
        1. 에러 로그 파일 저장
        2. 사용자에게 팝업 알림
        3. 프로그램 안전 종료
        """
        # 에러 메시지 생성
        error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        
        # 로그 파일 저장
        log_filename = self.save_error_log(error_msg)
        
        # 콘솔 출력
        print("=" * 70)
        print("🔥 CRITICAL ERROR DETECTED")
        print("=" * 70)
        print(error_msg)
        print(f"📝 Log saved: {log_filename}")
        print("=" * 70)
        
        # 사용자 알림 (GUI)
        self.show_error_dialog(error_msg, log_filename)
    
    def save_error_log(self, error_msg):
        """
        에러 로그를 파일로 저장
        
        Returns:
            str: 저장된 로그 파일 경로
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = os.path.join(self.log_dir, f"crash_log_{timestamp}.txt")
        
        with open(log_filename, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("Next-Gen AI Audio Workstation - Crash Report\n")
            f.write("=" * 70 + "\n")
            f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Python Version: {sys.version}\n")
            f.write("=" * 70 + "\n\n")
            f.write("ERROR DETAILS:\n")
            f.write("-" * 70 + "\n")
            f.write(error_msg)
            f.write("\n" + "=" * 70 + "\n")
        
        return log_filename
    
    def show_error_dialog(self, error_msg, log_filename):
        """
        사용자에게 에러 알림 대화상자 표시
        """
        # 에러 메시지 요약 (처음 3줄만)
        error_lines = error_msg.split('\n')
        error_summary = '\n'.join(error_lines[-3:])
        
        message = (
            "프로그램 실행 중 오류가 발생했습니다.\n\n"
            f"에러 요약:\n{error_summary}\n\n"
            f"상세 로그: {log_filename}\n\n"
            "프로그램을 종료합니다."
        )
        
        try:
            messagebox.showerror(
                "Critical Error",
                message
            )
        except:
            # GUI가 없는 경우 콘솔만 사용
            print(message)


# 전역 크래시 핸들러 인스턴스
crash_handler = None

def initialize_crash_handler():
    """
    크래시 핸들러 초기화
    프로그램 시작 시 한 번만 호출
    """
    global crash_handler
    crash_handler = CrashHandler()
    print("✅ Crash Handler initialized")


if __name__ == "__main__":
    # 테스트
    initialize_crash_handler()
    
    print("Testing crash handler...")
    
    # 의도적 에러 발생
    # result = 1 / 0  # ZeroDivisionError
    
    print("If you see this, crash handler is working!")
