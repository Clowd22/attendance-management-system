# =============================================================================
# ダミーデータ投入スクリプト
# -----------------------------------------------------------------------------
# 実行方法: .venv/bin/python -m app.seed
# 全件削除 → 再投入 の冪等な実装（何度実行しても同じ初期状態になる）。
# パブリックリポジトリのため、実在の人名・企業名は使わない。
# =============================================================================
from datetime import date, time

from sqlalchemy import delete

from app.core.security import hash_password
from app.db.session import SessionLocal, engine
from app.models import Base, Department, Employee, LeaveType, WorkSchedule


def seed_all() -> None:
    """ダミーデータを投入する。"""
    # テーブルが無ければ作る（マイグレーション未実行でも動作確認できるように）
    # ※通常は alembic upgrade head を使う。ここは学習用の保険。
    Base.metadata.create_all(engine)

    db = SessionLocal()
    try:
        # ---------- 既存データを全削除（子テーブル → 親テーブルの順） ----------
        db.execute(delete(Employee))
        db.execute(delete(LeaveType))
        db.execute(delete(WorkSchedule))
        db.execute(delete(Department))

        # ---------- 部署マスタ ----------
        dept_admin = Department(code="ADMIN", name="総務部", note="総務・人事を担当")
        dept_sales = Department(code="SALES", name="営業部")
        dept_eng = Department(code="ENG", name="開発部")
        db.add_all([dept_admin, dept_sales, dept_eng])

        # ---------- 勤務体系マスタ ----------
        std_schedule = WorkSchedule(
            code="STD",
            name="標準8時間勤務",
            start_time=time(9, 0),     # 09:00 始業
            end_time=time(18, 0),      # 18:00 終業
            required_minutes=480,      # 8 時間
            break_minutes=60,          # 休憩 1 時間
        )
        db.add(std_schedule)
        db.flush()  # id を確定させる（後続の社員から参照するため）

        # ---------- 休暇種別マスタ ----------
        leave_types = [
            LeaveType(code="PAID", name="年次有給休暇", grant_days=10, carryover=True, half_day=True),
            LeaveType(code="KEIGA", name="慶弔休暇", grant_days=5, carryover=False, half_day=False),
            LeaveType(code="SPECIAL", name="特別休暇", grant_days=3, carryover=False, half_day=True),
            LeaveType(code="KESSKI", name="欠勤", carryover=False, half_day=False),
        ]
        db.add_all(leave_types)

        # ---------- 社員マスタ（管理者1名 + 一般5名） ----------
        # パスワードは全員同じダミー値（bcrypt でハッシュ化して保存）
        password = hash_password("password123")

        # 共通項目（勤務体系・入社日・パスワード）はループ内でまとめて設定する
        employees_data = [
            # (社員番号, 姓, 名, 姓カナ, 名カナ, 部署, 雇用形態, ロール)
            ("E0001", "管理者", "太郎", "カンリシャ", "タロウ", dept_admin, "seishain", Employee.ROLE_ADMIN),
            ("E0002", "テスト", "太郎", "テスト", "タロウ", dept_eng, "seishain", Employee.ROLE_EMPLOYEE),
            ("E0003", "テスト", "花子", "テスト", "ハナコ", dept_eng, "seishain", Employee.ROLE_EMPLOYEE),
            ("E0004", "テスト", "次郎", "テスト", "ジロウ", dept_sales, "keiyaku", Employee.ROLE_EMPLOYEE),
            ("E0005", "テスト", "美咲", "テスト", "ミサキ", dept_sales, "arbeit", Employee.ROLE_EMPLOYEE),
            ("E0006", "テスト", "大輔", "テスト", "ダイスケ", dept_eng, "seishain", Employee.ROLE_EMPLOYEE),
        ]

        for (
            number, last, first, last_kana, first_kana,
            dept, emp_type, role,
        ) in employees_data:
            db.add(Employee(
                employee_number=number,
                last_name=last,
                first_name=first,
                last_name_kana=last_kana,
                first_name_kana=first_kana,
                department=dept,
                employment_type=emp_type,
                work_schedule=std_schedule,
                hire_date=date(2020, 4, 1),
                role=role,
                password_hash=password,
            ))

        # コミットして確定
        db.commit()
        print("シードデータを投入しました（社員 6 名）")
    finally:
        db.close()


if __name__ == "__main__":
    seed_all()