#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Image to PDF Converter with Size Limit
이미지 폴더를 선택하면 자동으로 150MB 이하의 PDF로 변환하는 프로그램
"""

import img2pdf
import os
import sys
from tkinter import Tk, filedialog, messagebox
from PIL import Image
import io
import tempfile

# 최대 파일 크기 (150MB)
MAX_FILE_SIZE = 150 * 1024 * 1024  # 150MB in bytes

def select_folder():
    """폴더 선택 다이얼로그 표시"""
    root = Tk()
    root.withdraw()  # 메인 윈도우 숨기기
    root.attributes('-topmost', True)  # 다이얼로그를 최상위로
    
    folder_path = filedialog.askdirectory(
        title="이미지가 들어있는 폴더를 선택하세요",
        initialdir=os.path.expanduser("~/Desktop")
    )
    
    root.destroy()
    return folder_path

def get_file_size_mb(file_path):
    """파일 크기를 MB 단위로 반환"""
    size_bytes = os.path.getsize(file_path)
    return size_bytes / (1024 * 1024)

def compress_image(image_path, quality=85):
    """이미지를 압축하여 임시 파일로 저장"""
    try:
        with Image.open(image_path) as img:
            # RGB 모드로 변환 (JPEG는 RGBA를 지원하지 않음)
            if img.mode in ('RGBA', 'LA', 'P'):
                # 흰색 배경 생성
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # 임시 파일로 저장
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
            img.save(temp_file.name, 'JPEG', quality=quality, optimize=True)
            temp_file.close()
            return temp_file.name
    except Exception as e:
        print(f"⚠️  이미지 압축 실패 ({os.path.basename(image_path)}): {e}")
        return image_path  # 원본 반환

def estimate_pdf_size(image_paths):
    """예상 PDF 크기 계산"""
    total_size = sum(os.path.getsize(p) for p in image_paths)
    return total_size

def convert_images_to_pdf(source_folder):
    """이미지를 150MB 이하의 PDF로 변환"""
    if not source_folder:
        print("❌ 폴더가 선택되지 않았습니다. 프로그램을 종료합니다.")
        return False
    
    print(f"📁 선택된 폴더: {source_folder}")
    
    # 출력 파일명 (선택한 폴더 내에 저장)
    output_filename = os.path.join(source_folder, "결과물.pdf")
    
    try:
        # 1. JPG/JPEG 파일만 골라내기
        all_files = os.listdir(source_folder)
        images = [
            f for f in all_files 
            if f.lower().endswith((".jpg", ".jpeg", ".png"))
        ]
        
        if not images:
            messagebox.showerror(
                "오류", 
                f"선택한 폴더에 이미지 파일이 없습니다.\n\n폴더: {source_folder}"
            )
            print("❌ 오류: 해당 폴더에 이미지 파일이 없습니다.")
            return False
        
        # 2. 파일 이름 순서대로 정렬
        images.sort()
        
        print(f"\n📸 발견된 이미지 파일 ({len(images)}개):")
        for idx, img in enumerate(images, 1):
            print(f"  {idx}. {img}")
        
        # 3. 전체 경로 생성
        images_path = [os.path.join(source_folder, img) for img in images]
        
        # 4. 원본 크기 확인
        original_size = estimate_pdf_size(images_path)
        print(f"\n📊 예상 원본 PDF 크기: {original_size / (1024*1024):.2f} MB")
        
        # 5. 압축이 필요한지 확인
        quality_levels = [95, 85, 75, 65, 55]  # 압축 품질 단계
        compressed_paths = []
        final_quality = 100
        
        if original_size > MAX_FILE_SIZE:
            print(f"⚠️  파일 크기가 150MB를 초과합니다. 압축을 시작합니다...\n")
            
            for quality in quality_levels:
                print(f"🔄 품질 {quality}%로 압축 중...")
                
                # 이전 압축 파일 삭제
                for path in compressed_paths:
                    try:
                        if path not in images_path:  # 원본이 아닌 경우만
                            os.unlink(path)
                    except:
                        pass
                compressed_paths = []
                
                # 모든 이미지 압축
                for idx, img_path in enumerate(images_path, 1):
                    print(f"  [{idx}/{len(images_path)}] {os.path.basename(img_path)}", end='\r')
                    compressed_path = compress_image(img_path, quality=quality)
                    compressed_paths.append(compressed_path)
                
                # 압축 후 크기 확인
                compressed_size = estimate_pdf_size(compressed_paths)
                print(f"\n  ✓ 압축 완료: {compressed_size / (1024*1024):.2f} MB")
                
                if compressed_size <= MAX_FILE_SIZE:
                    final_quality = quality
                    print(f"✅ 목표 크기 달성! (품질: {quality}%)\n")
                    break
            else:
                print(f"⚠️  최대 압축 후에도 150MB를 초과합니다.")
                print(f"   현재 크기: {compressed_size / (1024*1024):.2f} MB")
                print(f"   그래도 PDF를 생성합니다...\n")
                final_quality = quality_levels[-1]
            
            images_to_convert = compressed_paths
        else:
            print(f"✅ 원본 크기가 150MB 이하입니다. 압축 없이 진행합니다.\n")
            images_to_convert = images_path
        
        # 6. PDF 변환 및 저장
        print(f"🔄 PDF 변환 중...")
        with open(output_filename, "wb") as f:
            f.write(img2pdf.convert(images_to_convert))
        
        # 7. 임시 압축 파일 삭제
        for path in compressed_paths:
            try:
                if path not in images_path:  # 원본이 아닌 경우만
                    os.unlink(path)
            except:
                pass
        
        # 8. 최종 결과 확인
        final_size = get_file_size_mb(output_filename)
        
        if final_quality < 100:
            quality_info = f"\n압축 품질: {final_quality}%"
        else:
            quality_info = "\n압축: 없음 (원본 품질)"
        
        success_msg = (
            f"✅ 변환 완료!\n\n"
            f"이미지 수: {len(images)}장\n"
            f"최종 크기: {final_size:.2f} MB{quality_info}\n\n"
            f"저장 위치:\n{output_filename}"
        )
        
        print(f"\n{success_msg}")
        messagebox.showinfo("변환 완료", success_msg)
        
        # 결과 파일이 있는 폴더 열기
        try:
            os.startfile(source_folder)
        except:
            pass
        
        return True
        
    except PermissionError:
        error_msg = f"❌ 권한 오류: PDF 파일을 저장할 수 없습니다.\n\n'{output_filename}' 파일이 다른 프로그램에서 열려있는지 확인하세요."
        print(error_msg)
        messagebox.showerror("권한 오류", error_msg)
        return False
        
    except Exception as e:
        error_msg = f"❌ 오류가 발생했습니다:\n\n{str(e)}"
        print(error_msg)
        messagebox.showerror("오류", error_msg)
        return False

def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("  이미지 → PDF 변환기 (최대 150MB)")
    print("=" * 60)
    print("\n📂 이미지 폴더를 선택해주세요...\n")
    
    # 폴더 선택
    selected_folder = select_folder()
    
    # 변환 실행
    if selected_folder:
        convert_images_to_pdf(selected_folder)
    else:
        print("❌ 폴더 선택이 취소되었습니다.")
    
    print("\n" + "=" * 60)
    input("엔터 키를 누르면 종료합니다...")

if __name__ == "__main__":
    main()
