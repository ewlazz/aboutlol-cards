# 경기 후 평점 카드 생성기

`match.json` 하나로 4장(표지 / A팀 평점 / B팀 평점 / 아웃트로)을 만든다.

```
python3 make.py match.json        # out/<slug>/ 에 01~04 PNG + JPG
```

## match.json

| 키 | 설명 |
|---|---|
| slug | 출력 폴더 이름 (영문) |
| date | 표지 날짜, 예: 2027.01.15 |
| league | 표지 작은 글씨, 예: LCK 컵 1주차 |
| low_below | 이 점수 미만은 회색 (기본 6.0) |
| cover.photo | 표지 사진 경로 (없으면 검은 배경 + 로고/스코어) |
| cover.credit | 출처 (모르면 생략) |
| cover.focus_x / focus_y | 크롭 기준 0~1 (기본 0.5 / 0) |
| teams[] | 2팀. logo(assets/logos_white 파일명), name, score, players |
| players[] | 5명. pos(top/jungle/mid/bot/support), name, rating(0~10), pog(선택), note(선택 한줄평) |

로고: bfx dk dns drx geng hle kt ns t1 (한진 브리온은 없음 → 팀 이름 텍스트로 대체)
