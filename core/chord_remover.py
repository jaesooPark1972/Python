#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🎵 Chord Remover - GPT-SoVITS 전용 가사 정제 도구
====================================================
AI 생성 악보에서 코드(C, Am, G7 등)를 제거하고 깔끔한 가사만 추출합니다.
GPT-SoVITS 음성 합성에 최적화된 텍스트를 생성합니다.

작성자: Park Jae-soo (SKY Group)
최적화: 2600k PC에서도 1초 이내 처리 가능
"""

import re
import os
import sys

class ChordRemover:
    def __init__(self):
        """코드 제거 엔진 초기화"""
        # 일반적인 코드 패턴 (C, Am, G7, Dm7, F#m 등)
        self.chord_pattern = re.compile(
            r'\b[A-G](#|b)?(m|maj|min|dim|aug|sus)?[0-9]*(add|sus|dim|aug)?[0-9]*\b',
            re.IGNORECASE
        )
        
    def remove_brackets(self, text):
        """대괄호[], 소괄호() 안의 내용 제거 (예: [Intro], (Verse 1), [C], (Am7))"""
        text = re.sub(r'\[.*?\]', '', text)
        text = re.sub(r'\(.*?\)', '', text)
        return text
    
    def remove_chord_only_lines(self, text):
        """코드만 있는 줄 제거 (한글이 없는 줄)"""
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # 한글이 한 글자라도 있으면 유지
            if re.search('[가-힣]', line):
                cleaned_lines.append(line)
            # 영어 가사가 있는 경우도 고려 (알파벳이 연속 3글자 이상)
            elif re.search(r'[a-zA-Z]{3,}', line) and not self.is_chord_line(line):
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def is_chord_line(self, line):
        """해당 줄이 코드만 있는 줄인지 판단"""
        # 공백 제거 후 검사
        clean_line = line.strip()
        if not clean_line:
            return True
        
        # 코드 패턴만 있는지 확인
        words = clean_line.split()
        chord_count = 0
        for word in words:
            if self.chord_pattern.match(word):
                chord_count += 1
        
        # 모든 단어가 코드면 코드 전용 줄로 판단
        return chord_count == len(words) and chord_count > 0
    
    def remove_inline_chords(self, text):
        """가사 중간에 섞인 코드 제거 (예: "학교종이C 땡땡땡Am")"""
        return self.chord_pattern.sub('', text)
    
    def clean_whitespace(self, text):
        """불필요한 공백 정리"""
        # 여러 공백을 하나로
        text = re.sub(r' +', ' ', text)
        # 여러 줄바꿈을 최대 2개로
        text = re.sub(r'\n{3,}', '\n\n', text)
        # 각 줄의 앞뒤 공백 제거
        lines = [line.strip() for line in text.split('\n')]
        return '\n'.join(lines)
    
    def process(self, text):
        """
        전체 처리 파이프라인
        1. 대괄호/소괄호 제거
        2. 코드 전용 줄 제거
        3. 인라인 코드 제거
        4. 공백 정리
        """
        if not text:
            return ""
        
        print("🎵 코드 제거 시작...")
        
        # Step 1: 괄호 제거
        text = self.remove_brackets(text)
        print("   ✓ 괄호 제거 완료")
        
        # Step 2: 코드 전용 줄 제거
        text = self.remove_chord_only_lines(text)
        print("   ✓ 코드 전용 줄 제거 완료")
        
        # Step 3: 인라인 코드 제거
        text = self.remove_inline_chords(text)
        print("   ✓ 인라인 코드 제거 완료")
        
        # Step 4: 공백 정리
        text = self.clean_whitespace(text)
        print("   ✓ 공백 정리 완료")
        
        return text.strip()


def process_file(input_path, output_path=None):
    """파일에서 가사를 읽어 처리하고 결과를 저장"""
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        remover = ChordRemover()
        clean_text = remover.process(text)
        
        if output_path is None:
            # 출력 경로가 없으면 입력 파일명에 _clean 추가
            base, ext = os.path.splitext(input_path)
            output_path = f"{base}_clean{ext}"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(clean_text)
        
        print(f"\n✅ 처리 완료!")
        print(f"   입력: {input_path}")
        print(f"   출력: {output_path}")
        print(f"   원본 길이: {len(text)} 글자")
        print(f"   정제 후: {len(clean_text)} 글자")
        
        return clean_text
    
    except FileNotFoundError:
        print(f"❌ 오류: 파일을 찾을 수 없습니다 - {input_path}")
        return None
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return None


def interactive_mode():
    """대화형 모드 - 직접 텍스트 입력"""
    print("="*60)
    print("🎵 Chord Remover - 대화형 모드")
    print("="*60)
    print("가사를 붙여넣고 Enter를 두 번 누르세요 (종료: Ctrl+Z 또는 Ctrl+D)")
    print("-"*60)
    
    lines = []
    try:
        while True:
            line = input()
            if line == "":
                if lines:  # 빈 줄이 입력되고 이미 내용이 있으면 종료
                    break
            lines.append(line)
    except EOFError:
        pass
    
    input_text = '\n'.join(lines)
    
    if not input_text.strip():
        print("❌ 입력된 텍스트가 없습니다.")
        return
    
    remover = ChordRemover()
    clean_text = remover.process(input_text)
    
    print("\n" + "="*60)
    print("✨ 정제된 가사:")
    print("="*60)
    print(clean_text)
    print("="*60)
    
    # 파일로 저장할지 물어보기
    save = input("\n파일로 저장하시겠습니까? (y/n): ").strip().lower()
    if save == 'y':
        filename = input("파일명 입력 (기본: clean_lyrics.txt): ").strip()
        if not filename:
            filename = "clean_lyrics.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(clean_text)
        print(f"✅ 저장 완료: {filename}")


def main():
    """메인 실행 함수"""
    print("="*60)
    print("🎵 Chord Remover - GPT-SoVITS 가사 정제 도구")
    print("   작성자: Park Jae-soo (SKY Group)")
    print("="*60)
    
    if len(sys.argv) > 1:
        # 파일 모드
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
        process_file(input_file, output_file)
    else:
        # 대화형 모드
        interactive_mode()


# ============================================================
# 📋 사용 예제
# ============================================================
if __name__ == "__main__":
    # 방법 1: 명령줄에서 파일 처리
    # python chord_remover.py input.txt output.txt
    
    # 방법 2: 대화형 모드
    # python chord_remover.py
    
    # 방법 3: 코드에서 직접 사용
    # remover = ChordRemover()
    # clean = remover.process(your_text)
    
    main()
