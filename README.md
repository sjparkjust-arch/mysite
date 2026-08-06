# Django File Board

Django 기반의 파일 자료실 게시판 실습 프로젝트입니다.

회원가입과 로그인, 게시글 작성·수정·삭제, 검색과 페이지네이션, 다중 첨부파일 업로드 및 다운로드 기능을 구현합니다. 기본 데이터베이스는 SQLite이며, 환경변수 설정과 Django 설정 변경을 통해 MariaDB로 전환할 수 있습니다.

## 주요 기능

- 회원가입, 로그인, 로그아웃
- 게시글 목록 및 상세 조회
- 게시글 작성, 수정, 삭제
- 작성자 본인만 게시글 수정·삭제 가능
- 제목, 작성자, 내용 및 통합 검색
- 게시글 목록 페이지네이션
- 조회수 증가
- 다중 첨부파일 업로드
- 기존 첨부파일 선택 삭제
- 첨부파일 다운로드
- 파일 확장자, MIME 형식 및 최대 크기 검증
- Django Messages Framework를 이용한 처리 결과 안내

## 기술 구성

| 구분 | 사용 기술 |
|---|---|
| Backend | Python, Django 6.0.6 |
| Database | SQLite 기본, MariaDB 전환 가능 |
| Frontend | Django Template, HTML, CSS |
| Authentication | Django Authentication |
| File Storage | Django FileField, 로컬 `media/` |
| Environment | python-dotenv |

## 프로젝트 구조

```text
fileboard/
├── board/
│   ├── migrations/
│   ├── static/board/
│   ├── templates/board/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── media/
│   └── attachments/
├── .env.example
├── .gitignore
├── manage.py
└── requirements.txt
```

## 데이터 모델

### Post

| 필드 | 설명 |
|---|---|
| `title` | 게시글 제목, 최대 100자 |
| `content` | 게시글 내용 |
| `author` | 작성자 |
| `view_count` | 조회수 |
| `created_at` | 작성 일시 |
| `updated_at` | 수정 일시 |

### Attachment

| 필드 | 설명 |
|---|---|
| `post` | 연결된 게시글 |
| `file` | 저장된 첨부파일 |
| `original_name` | 업로드 당시 원본 파일명 |
| `uploaded_at` | 업로드 일시 |

첨부파일은 다음과 같은 경로에 UUID 기반 파일명으로 저장됩니다.

```text
media/attachments/<게시글 ID>/<UUID>.<확장자>
```

## 실행 환경

- Python 3.12 이상 권장
- Django 6.0.6
- pip
- Git

## 설치 및 실행

### 1. 저장소 복제

```bash
git clone https://github.com/itthisgo/fileboard.git
cd fileboard
```

### 2. 가상환경 생성

#### Ubuntu / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

#### Windows PowerShell

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

PowerShell 실행 정책 때문에 활성화되지 않으면 현재 사용자 범위에서 실행 정책을 변경합니다.

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### 3. 패키지 설치

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. 환경변수 파일 생성

#### Ubuntu / macOS

```bash
cp .env.example .env
```

#### Windows PowerShell

```powershell
Copy-Item .env.example .env
```

`.env` 파일을 다음과 같이 설정합니다.

```env
DJANGO_SECRET_KEY=개발용-시크릿키
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost

DB_ENGINE=django.db.backends.mysql
DB_NAME=fileboard
DB_USER=fileboard
DB_PASSWORD=비밀번호
DB_HOST=127.0.0.1
DB_PORT=3306

STATIC_ROOT=staticfiles
MEDIA_ROOT=media
```

현재 기본 설정은 SQLite를 사용하므로 MariaDB 관련 값은 SQLite 실행 시 사용되지 않습니다.

장고에 설정하는 Secret Key는 python manage.py shell 실행 후 다음 명령으로 생성할 수 있습니다.

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

또는 https://djecrety.ir/ 에서 생성할 수 있습니다.

<b>Secret Key 키는 공개하면 안됩니다.</b>

### 5. 데이터베이스 마이그레이션

```bash
python manage.py migrate
```

### 6. 관리자 계정 생성

```bash
python manage.py createsuperuser
```

### 7. 개발 서버 실행

```bash
python manage.py runserver
```

브라우저에서 다음 주소로 접속합니다.

```text
http://127.0.0.1:8000/
```

관리자 페이지:

```text
http://127.0.0.1:8000/admin/
```

## MariaDB 사용

현재 `config/settings.py`는 SQLite 구성을 기본값으로 사용하고, MariaDB 설정 예시는 주석으로 포함하고 있습니다.

MariaDB로 전환하려면 먼저 시스템 패키지와 Python 드라이버를 설치합니다.

### Ubuntu

```bash
sudo apt update
sudo apt install mariadb-server libmariadb-dev build-essential pkg-config -y
pip install mysqlclient
```

### Windows

Windows에서는 MariaDB 서버를 설치한 뒤 다음 명령을 실행합니다.

```powershell
pip install mysqlclient
```

환경에 따라 `mysqlclient` 빌드 오류가 발생하면 Python 버전과 호환되는 빌드 도구 또는 사전 빌드 패키지가 필요할 수 있습니다.

MariaDB 데이터베이스와 사용자를 생성합니다.

```sql
CREATE DATABASE fileboard
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

CREATE USER 'fileboard'@'localhost'
    IDENTIFIED BY '비밀번호';

GRANT ALL PRIVILEGES
    ON fileboard.*
    TO 'fileboard'@'localhost';

FLUSH PRIVILEGES;
```

그다음 `config/settings.py`의 SQLite 설정을 MariaDB 설정으로 변경합니다.

```python
DATABASES = {
    "default": {
        "ENGINE": os.getenv(
            "DB_ENGINE",
            "django.db.backends.mysql",
        ),
        "NAME": os.environ["DB_NAME"],
        "USER": os.environ["DB_USER"],
        "PASSWORD": os.environ["DB_PASSWORD"],
        "HOST": os.getenv("DB_HOST", "127.0.0.1"),
        "PORT": os.getenv("DB_PORT", "3306"),
        "OPTIONS": {
            "charset": "utf8mb4",
        },
    }
}
```

변경 후 마이그레이션을 실행합니다.

```bash
python manage.py migrate
```

## 파일 업로드 정책

파일 한 개당 최대 크기는 20MB입니다.

허용 확장자:
```text
.pdf, .txt, .doc, .docx, .xls, .xlsx,
.ppt, .pptx, .zip, .png, .jpg, .jpeg
```

허용 MIME type:
```text
"application/pdf",
"text/plain",
"application/msword",
"application/vnd.openxmlformats-officedocument.wordprocessingml.document",
"application/vnd.ms-excel",
"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
"application/vnd.ms-powerpoint",
"application/vnd.openxmlformats-officedocument.presentationml.presentation",
"application/zip",
"application/x-zip-compressed",
"image/png",
"image/jpeg",
```

파일 업로드 시 다음 항목을 검사합니다.

- 파일 크기
- 파일 확장자
- 브라우저가 전달한 MIME 형식

MIME 형식은 클라이언트가 전달하는 값이므로, 외부 공개 서비스에서는 파일 시그니처 검사와 악성코드 검사 같은 추가 보안 대책이 필요합니다.

## 주요 URL

| URL | 기능 |
|---|---|
| `/` | 게시글 목록 |
| `/posts/add/` | 게시글 작성 |
| `/posts/<id>/` | 게시글 상세 |
| `/posts/<id>/update/` | 게시글 수정 |
| `/posts/<id>/delete/` | 게시글 삭제 |
| `/attachments/<id>/download/` | 첨부파일 다운로드 |
| `/signin/` | 로그인 |
| `/signout/` | 로그아웃 |
| `/signup/` | 회원가입 |
| `/admin/` | Django 관리자 |

## 정적 파일 수집

Nginx와 Gunicorn을 사용하는 운영 환경에서는 정적 파일을 한곳에 모읍니다.

```bash
python manage.py collectstatic
```

기본 수집 경로:

```text
staticfiles/
```

업로드 파일 기본 경로:

```text
media/
```

## 운영 배포 시 확인사항

개발 서버는 운영용으로 사용하지 않습니다.

운영 환경에서는 다음 항목을 별도로 구성해야 합니다.

- `DJANGO_DEBUG=False`
- 충분히 복잡한 `DJANGO_SECRET_KEY`
- 실제 도메인 또는 서버 IP를 `DJANGO_ALLOWED_HOSTS`에 등록
- Gunicorn 또는 다른 WSGI 서버 사용
- Nginx Reverse Proxy 구성
- `/static/` 정적 파일 경로 설정
- `/media/` 첨부파일 경로 또는 보호된 다운로드 구성
- HTTPS 적용
- MariaDB 계정 최소 권한 설정
- 업로드 파일 실행 차단
- 데이터베이스와 첨부파일 백업

Gunicorn을 추가로 설치한 경우 실행 예시는 다음과 같습니다.

```bash
pip install gunicorn
gunicorn --bind 127.0.0.1:8000 config.wsgi:application
```

> 현재 `requirements.txt`에는 Gunicorn과 MariaDB용 `mysqlclient`가 포함되어 있지 않습니다. 운영 구성에 사용할 경우 설치 후 `requirements.txt`에 추가하는 것을 권장합니다.

## Git 사용 시 주의사항

다음 파일과 디렉터리는 저장소에 올리지 않는 것이 좋습니다.

```gitignore
.env
venv/
.venv/
__pycache__/
*.pyc
staticfiles/
media/
```

실제 Secret Key, 데이터베이스 비밀번호, 운영 서버 정보가 포함된 `.env` 파일은 GitHub에 업로드하지 않습니다.

## 학습 포인트

이 프로젝트를 통해 다음 내용을 실습할 수 있습니다.

- Django 프로젝트와 앱 구조
- URL과 View 연결
- Django ORM과 모델 관계
- 회원 인증과 접근 제어
- CRUD 구현
- 파일 업로드 및 다운로드
- 검색과 페이지네이션
- `select_related()`와 `prefetch_related()` 조회 최적화
- `F()` 표현식을 이용한 조회수 증가
- `transaction.atomic()` 트랜잭션 처리
- 환경변수를 이용한 설정 분리
- SQLite에서 MariaDB로 데이터베이스 전환
- Nginx, Gunicorn 및 NFS 연계 확장

## 제작

- 제작: IT핥기
- YouTube: [IT핥기 유튜브 채널](https://www.youtube.com/@it핥기)
- Repository: [itthisgo/fileboard](https://github.com/itthisgo/fileboard)

## 라이선스

현재 저장소에는 별도의 라이선스 파일이 포함되어 있지 않습니다. 재사용이나 배포 전에 저장소 소유자의 사용 조건을 확인하세요.

---

&copy; 2026 IT핥기. All rights reserved.
