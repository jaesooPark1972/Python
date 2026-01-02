# 🎵 Chord Remover 사용 가이드

## 📌 개요

AI로 만든 악보에서 코드(C, Am, G7 등)를 제거하고 깔끔한 가사만 추출하는 도구입니다.
GPT-SoVITS 음성 합성에 최적화된 텍스트를 생성합니다.

## 🚀 사용 방법

### 방법 1: 대화형 모드 (가장 간단!)

```bash
python chord_remover.py
```

1. 프로그램 실행
2. 지저분한 악보/가사를 복사해서 붙여넣기
3. Enter 두 번 누르기
4. 깔끔한 결과 확인!

### 방법 2: 파일 처리

```bash
# 기본 사용 (자동으로 _clean 파일 생성)
python chord_remover.py input.txt

# 출력 파일명 지정
python chord_remover.py input.txt output.txt
```

### 방법 3: 다른 파이썬 코드에서 사용

```python
from chord_remover import ChordRemover

remover = ChordRemover()
clean_text = remover.process(your_dirty_text)
print(clean_text)
```

## ✨ 기능

### 1. 괄호 제거

- `[Intro]`, `[Verse 1]`, `[Chorus]` 등 섹션 표시 제거
- `(C)`, `(Am7)` 등 괄호 안의 코드 제거

### 2. 코드 전용 줄 제거

```
C  G  Am  F          ← 이런 줄 완전 삭제
학교종이 땡땡땡      ← 이런 줄은 유지
```

### 3. 인라인 코드 제거

```
학교종이C 땡땡땡G    →  학교종이 땡땡땡
```

### 4. 복잡한 코드도 인식

- 기본: C, D, E, F, G, A, B
- 변형: C#, Db, F#m
- 7th: C7, Am7, Cmaj7
- 기타: Csus4, Cdim, Caug

## 📊 테스트 결과

### 테스트 1: 기본 악보

**입력:**

```
[Intro]
C  G  Am  F

(Verse 1)
C        G
학교종이 땡땡땡
Am       F
어서 모이자
```

**출력:**

```
학교종이 땡땡땡
어서 모이자
```

### 테스트 2: 영어 가사

**입력:**

```
[Verse 1]
C           G
Hello darkness my old friend
Am              F
I've come to talk with you again
```

**출력:**

```
Hello darkness my old friend
I've come to talk with you again
```

## 💡 활용 예시

### GPT-SoVITS 준비

1. Suno AI에서 생성한 가사 복사
2. `chord_remover.py` 실행
3. 가사 붙여넣기
4. 정제된 텍스트를 GPT-SoVITS에 입력

### 대량 파일 처리

```bash
# 여러 파일 한 번에 처리
for file in *.txt; do
    python chord_remover.py "$file"
done
```

## 🔧 기술 사양

- **언어**: Python 3.6+
- **의존성**: 없음 (표준 라이브러리만 사용)
- **성능**: 2600k PC에서도 1초 이내 처리
- **인코딩**: UTF-8 (한글 완벽 지원)

## 📝 주의사항

- 한글 가사는 무조건 보존됩니다
- 영어 가사는 3글자 이상 연속된 단어만 보존됩니다
- 코드와 가사가 붙어있으면 (`학교종이C`) 코드만 제거됩니다

## 🎯 기존 코드와의 차이점

### 사용자가 제공한 코드

- ✅ 간단하고 직관적
- ❌ 인라인 코드 처리 안 됨
- ❌ 영어 가사 처리 약함

### 우리가 만든 코드

- ✅ 모든 코드 패턴 인식 (C, Am7, F#dim 등)
- ✅ 인라인 코드 제거
- ✅ 한글/영어 가사 모두 지원
- ✅ 파일 모드 + 대화형 모드
- ✅ 테스트 코드 포함
- ✅ 기존 프로젝트 스타일 반영

## 🎓 작성자

Park Jae-soo (SKY Group)

- 기존 `master_score_maker.py`, `score_maker.py`의 가사 정제 로직 개선
- GPT-SoVITS 워크플로우 최적화
