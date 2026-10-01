from http.server import BaseHTTPRequestHandler, HTTPServer
import sqlite3
from urllib.parse import parse_qs

class Handler(BaseHTTPRequestHandler):

    def page(self, content):
        html = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>فرص ومشاريع</title>
<style>
body{{font-family:Arial;background:#f4f6f8;margin:0;padding:20px}}
.box{{max-width:600px;margin:auto;background:white;padding:25px;border-radius:18px}}
h1{{margin-top:0}}
input,select,button{{width:100%;padding:14px;margin:8px 0;box-sizing:border-box;border-radius:10px;border:1px solid #ddd}}
button{{background:#111;color:white;border:0;font-size:16px}}
.card{{background:#f5f5f5;padding:15px;margin-top:15px;border-radius:12px}}
</style>
</head>
<body>
<div class="box">
{content}
</div>
</body>
</html>"""
        return html

    def send_html(self, html):
        self.send_response(200)
        self.send_header("Content-Type","text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def show_project(self, project_id):
        conn = sqlite3.connect("projects.db")
        cur = conn.cursor()

        cur.execute("""
            SELECT name, category, min_capital, startup_cost,
                   monthly_cost, expected_revenue, description,
                   steps, requirements, effort
            FROM projects
            WHERE id = ?
        """, (project_id,))

        project = cur.fetchone()
        conn.close()

        if not project:
            self.send_html(self.page(
                "<h1>المشروع غير موجود ❌</h1>"
                "<p><a href='/'>العودة</a></p>"
            ))
            return

        (name, category, min_capital, startup, monthly,
         revenue, description, steps, requirements, effort) = project

        profit = revenue - monthly

        if profit > 0:
            break_even = round(startup / profit, 1)
            break_even_text = f"{break_even} شهر تقريبًا"
        else:
            break_even_text = "غير متاح"

        content = f"""
        <h1>{name}</h1>

        <div class="card">
            <h2>📋 معلومات المشروع</h2>

            <p>📂 المجال: {category}</p>
            <p>💰 الحد الأدنى لرأس المال: {min_capital} ريال</p>
            <p>💵 تكلفة البداية: {startup} ريال</p>
            <p>📦 المصاريف الشهرية: {monthly} ريال</p>
            <p>📈 الإيراد المتوقع: {revenue} ريال شهرياً</p>
            <p>💰 الربح التقديري: {profit} ريال شهرياً</p>
            <p>⏳ نقطة التعادل التقديرية: {break_even_text}</p>
            <p>💪 مستوى الجهد: {effort}/5</p>

            <hr>

            <h3>🧰 المتطلبات</h3>
            <p>{requirements}</p>

            <h3>📝 خطوات البدء</h3>
            <p>{steps}</p>

            <h3>📖 وصف المشروع</h3>
            <p>{description}</p>

            <br>

            <form method="POST" action="/favorite">
                <input type="hidden" name="project_id" value="{project_id}">
                <button type="submit">⭐ حفظ المشروع</button>
            </form>
        </div>

        <br>
        <a href="/">← العودة للمشاريع</a>
        """

        self.send_html(self.page(content))

    def show_favorites(self):
        user_id = self.get_current_user()

        if not user_id:
            self.redirect("/login")
            return

        conn = sqlite3.connect("projects.db")
        cur = conn.cursor()

        cur.execute("""
            SELECT projects.id,
                   projects.name,
                   projects.category,
                   projects.startup_cost,
                   projects.expected_revenue,
                   projects.description
            FROM favorites
            JOIN projects ON projects.id = favorites.project_id
            WHERE favorites.user_id = ?
            ORDER BY favorites.created_at DESC
        """, (user_id,))

        rows = cur.fetchall()
        conn.close()

        if not rows:
            cards = "<p>لا توجد مشاريع محفوظة حتى الآن ⭐</p>"
        else:
            cards = ""

            for project_id, name, category, startup, revenue, description in rows:
                cards += f"""
                <div class="card">
                    <h2>⭐ {name}</h2>
                    <p>📂 المجال: {category}</p>
                    <p>💰 تكلفة البداية: {startup} ريال</p>
                    <p>📈 الإيراد المتوقع: {revenue} ريال شهرياً</p>
                    <p>{description}</p>

                    <form method="POST" action="/remove_favorite">
                        <input type="hidden" name="project_id"
                               value="{project_id}">
                        <button type="submit">🗑️ إزالة من المفضلة</button>
                    </form>
                </div>
                """

        content = f"""
        <h1>مشاريعي المحفوظة ⭐</h1>
        {cards}
        <br>
        <a href="/">← العودة للبحث</a>
        """

        self.send_html(self.page(content))

    def login_page(self):
        content = """
        <h1>تسجيل الدخول 🔐</h1>

        <p>اكتب رقم الجوال المستخدم عند إنشاء الحساب.</p>

        <form method="POST" action="/login">
            <input name="phone"
                   type="text"
                   placeholder="رقم الجوال"
                   required>

            <button type="submit">دخول</button>
        </form>

        <p>
            ليس لديك حساب؟
            <a href="/register">إنشاء حساب</a>
        </p>
        """

        self.send_html(self.page(content))

    def do_GET(self):
        if self.path == "/login":
            self.login_page()
            return

        if self.path.startswith("/project/"):
            try:
                project_id = int(self.path.split("/project/")[1])
                self.show_project(project_id)
            except (ValueError, IndexError):
                self.send_html(self.page("<h1>رقم المشروع غير صحيح ❌</h1>"))
            return

        if self.path == "/favorites":
            self.show_favorites()
            return

        if self.path == "/register":
            content = """
            <h1>إنشاء حساب 👤</h1>
            <p>أنشئ حسابك لحفظ مشاريعك المفضلة.</p>

            <form method="POST" action="/register">
                <input name="name" type="text"
                placeholder="الاسم" required>

                <input name="phone" type="text"
                placeholder="رقم الجوال" required>

                <button type="submit">إنشاء الحساب</button>
            </form>

            <p><a href="/">العودة للبحث</a></p>
            """
            self.send_html(self.page(content))
            return

        content = """
        <h1>فرص ومشاريع 🚀</h1>
          <p>
              <a href="/favorites">
                  ⭐ مشاريعي المحفوظة
              </a>
          </p>
        <p>أدخل بياناتك لنبحث عن المشاريع المناسبة لك.</p>

        <form method="POST">

        <input name="capital" type="number"
        placeholder="رأس المال بالريال" required>

        <input name="hours" type="number"
        placeholder="ساعات العمل يومياً" required>

        <input name="city" type="text"
        placeholder="المدينة" required>

        <select name="place">
        <option value="home">من المنزل</option>
        <option value="shop">محل / موقع</option>
        </select>

        <select name="category">
        <option value="all">كل المجالات</option>
        <option value="تجارة إلكترونية">تجارة إلكترونية</option>
        <option value="خدمات رقمية">خدمات رقمية</option>
        <option value="تجارة">تجارة</option>
        <option value="خدمات">خدمات</option>
        </select>

        <button type="submit">ابحث عن المشاريع 🔎</button>
        </form>
        """

        self.send_html(self.page(content))

    def register_user(self, name, phone):
        conn = sqlite3.connect("projects.db")
        cur = conn.cursor()

        try:
            cur.execute(
                "INSERT INTO users (name, phone) VALUES (?, ?)",
                (name, phone)
            )
            conn.commit()
            result = "تم إنشاء حسابك بنجاح ✅"
        except sqlite3.IntegrityError:
            result = "رقم الجوال مستخدم بالفعل ⚠️"

        conn.close()

        self.send_html(self.page(
            f"<h1>{result}</h1><p><a href='/'>العودة للتطبيق</a></p>"
        ))

    def remove_favorite(self, project_id):
        user_id = self.get_current_user()

        if not user_id:
            self.redirect("/login")
            return

        conn = sqlite3.connect("projects.db")
        cur = conn.cursor()

        cur.execute(
            "DELETE FROM favorites WHERE user_id = ? AND project_id = ?",
            (user_id, project_id)
        )

        conn.commit()
        conn.close()

        self.send_html(self.page(
            "<h1>تم حذف المشروع من المفضلة 🗑️</h1>"
            "<p><a href='/favorites'>العودة للمفضلة</a></p>"
        ))

    def show_project(self, project_id):
        conn = sqlite3.connect("projects.db")
        cur = conn.cursor()

        cur.execute("""
            SELECT name, category, min_capital, startup_cost,
                   monthly_cost, expected_revenue, description,
                   steps, requirements, effort
            FROM projects
            WHERE id = ?
        """, (project_id,))

        project = cur.fetchone()
        conn.close()

        if not project:
            self.send_html(self.page(
                "<h1>المشروع غير موجود ❌</h1>"
                "<p><a href='/'>العودة</a></p>"
            ))
            return

        (name, category, min_capital, startup, monthly,
         revenue, description, steps, requirements, effort) = project

        profit = revenue - monthly

        if profit > 0:
            break_even = round(startup / profit, 1)
            break_even_text = f"{break_even} شهر تقريبًا"
        else:
            break_even_text = "غير متاح"

        content = f"""
        <h1>{name}</h1>

        <div class="card">
            <h2>📋 معلومات المشروع</h2>

            <p>📂 المجال: {category}</p>
            <p>💰 الحد الأدنى لرأس المال: {min_capital} ريال</p>
            <p>💵 تكلفة البداية: {startup} ريال</p>
            <p>📦 المصاريف الشهرية: {monthly} ريال</p>
            <p>📈 الإيراد المتوقع: {revenue} ريال شهرياً</p>
            <p>💰 الربح التقديري: {profit} ريال شهرياً</p>
            <p>⏳ نقطة التعادل التقديرية: {break_even_text}</p>
            <p>💪 مستوى الجهد: {effort}/5</p>

            <hr>

            <h3>🧰 المتطلبات</h3>
            <p>{requirements}</p>

            <h3>📝 خطوات البدء</h3>
            <p>{steps}</p>

            <h3>📖 وصف المشروع</h3>
            <p>{description}</p>

            <br>

            <form method="POST" action="/favorite">
                <input type="hidden" name="project_id" value="{project_id}">
                <button type="submit">⭐ حفظ المشروع</button>
            </form>
        </div>

        <br>
        <a href="/">← العودة للمشاريع</a>
        """

        self.send_html(self.page(content))

    def show_favorites(self):
        conn = sqlite3.connect("projects.db")
        cur = conn.cursor()

        cur.execute("""
            SELECT projects.id,
                   projects.name,
                   projects.category,
                   projects.startup_cost,
                   projects.expected_revenue,
                   projects.description
            FROM favorites
            JOIN projects ON projects.id = favorites.project_id
            ORDER BY favorites.created_at DESC
        """)

        rows = cur.fetchall()
        conn.close()

        if not rows:
            cards = "<p>لا توجد مشاريع محفوظة حتى الآن ⭐</p>"
        else:
            cards = ""

            for project_id, name, category, startup, revenue, description in rows:
                cards += f"""
                <div class="card">
                    <h2>⭐ {name}</h2>
                    <p>📂 المجال: {category}</p>
                    <p>💰 تكلفة البداية: {startup} ريال</p>
                    <p>📈 الإيراد المتوقع: {revenue} ريال شهرياً</p>
                    <p>{description}</p>

                    <form method="POST" action="/remove_favorite">
                        <input type="hidden" name="project_id"
                               value="{project_id}">
                        <button type="submit">🗑️ إزالة من المفضلة</button>
                    </form>
                </div>
                """

        content = f"""
        <h1>مشاريعي المحفوظة ⭐</h1>
        {cards}
        <br>
        <a href="/">← العودة للبحث</a>
        """

        self.send_html(self.page(content))

    def login_page(self):
        content = """
        <h1>تسجيل الدخول 🔐</h1>

        <p>اكتب رقم الجوال المستخدم عند إنشاء الحساب.</p>

        <form method="POST" action="/login">
            <input name="phone"
                   type="text"
                   placeholder="رقم الجوال"
                   required>

            <button type="submit">دخول</button>
        </form>

        <p>
            ليس لديك حساب؟
            <a href="/register">إنشاء حساب</a>
        </p>
        """

        self.send_html(self.page(content))

    def do_GET(self):
        if self.path == "/login":
            self.login_page()
            return

        if self.path.startswith("/project/"):
            try:
                project_id = int(self.path.split("/project/")[1])
                self.show_project(project_id)
            except (ValueError, IndexError):
                self.send_html(self.page("<h1>رقم المشروع غير صحيح ❌</h1>"))
            return

        if self.path == "/favorites":
            self.show_favorites()
            return

        if self.path == "/register":
            content = """
            <h1>إنشاء حساب 👤</h1>
            <p>أنشئ حسابك لحفظ مشاريعك المفضلة.</p>

            <form method="POST" action="/register">
                <input name="name" type="text"
                placeholder="الاسم" required>

                <input name="phone" type="text"
                placeholder="رقم الجوال" required>

                <button type="submit">إنشاء الحساب</button>
            </form>

            <p><a href="/">العودة للبحث</a></p>
            """
            self.send_html(self.page(content))
            return

        content = """
        <h1>فرص ومشاريع 🚀</h1>
          <p>
              <a href="/favorites">
                  ⭐ مشاريعي المحفوظة
              </a>
          </p>
        <p>أدخل بياناتك لنبحث عن المشاريع المناسبة لك.</p>

        <form method="POST">

        <input name="capital" type="number"
        placeholder="رأس المال بالريال" required>

        <input name="hours" type="number"
        placeholder="ساعات العمل يومياً" required>

        <input name="city" type="text"
        placeholder="المدينة" required>

        <select name="place">
        <option value="home">من المنزل</option>
        <option value="shop">محل / موقع</option>
        </select>

        <select name="category">
        <option value="all">كل المجالات</option>
        <option value="تجارة إلكترونية">تجارة إلكترونية</option>
        <option value="خدمات رقمية">خدمات رقمية</option>
        <option value="تجارة">تجارة</option>
        <option value="خدمات">خدمات</option>
        </select>

        <button type="submit">ابحث عن المشاريع 🔎</button>
        </form>
        """

        self.send_html(self.page(content))

    def register_user(self, name, phone):
        conn = sqlite3.connect("projects.db")
        cur = conn.cursor()

        try:
            cur.execute(
                "INSERT INTO users (name, phone) VALUES (?, ?)",
                (name, phone)
            )
            conn.commit()
            result = "تم إنشاء حسابك بنجاح ✅"
        except sqlite3.IntegrityError:
            result = "رقم الجوال مستخدم بالفعل ⚠️"

        conn.close()

        self.send_html(self.page(
            f"<h1>{result}</h1><p><a href='/'>العودة للتطبيق</a></p>"
        ))

    def remove_favorite(self, project_id):
        conn = sqlite3.connect("projects.db")
        cur = conn.cursor()

        cur.execute("SELECT id FROM users ORDER BY id DESC LIMIT 1")
        user = cur.fetchone()

        if not user:
            conn.close()
            self.send_html(self.page(
                "<h1>لا يوجد حساب ⚠️</h1>"
                "<p><a href='/register'>إنشاء حساب</a></p>"
            ))
            return

        cur.execute(
            "DELETE FROM favorites WHERE user_id = ? AND project_id = ?",
            (user[0], project_id)
        )

        conn.commit()
        conn.close()

        self.send_html(self.page(
            "<h1>تم حذف المشروع من المفضلة 🗑️</h1>"
            "<p><a href='/favorites'>العودة للمفضلة</a></p>"
        ))

    def get_current_user(self):
        from http.cookies import SimpleCookie

        cookie = SimpleCookie()
        cookie.load(self.headers.get("Cookie", ""))

        if "user_id" not in cookie:
            return None

        try:
            return int(cookie["user_id"].value)
        except ValueError:
            return None

    def redirect(self, path):
        self.send_response(302)
        self.send_header("Location", path)
        self.end_headers()

    def save_favorite(self, project_id):
        user_id = self.get_current_user()

        if not user_id:
            self.redirect("/login")
            return

        conn = sqlite3.connect("projects.db")
        cur = conn.cursor()

        try:
            cur.execute(
                "INSERT INTO favorites (user_id, project_id) VALUES (?, ?)",
                (user_id, project_id)
            )
            conn.commit()
            message = "تم حفظ المشروع في المفضلة ⭐"
        except sqlite3.IntegrityError:
            message = "المشروع محفوظ بالفعل ⭐"

        conn.close()

        self.send_html(self.page(
            f"<h1>{message}</h1>"
            "<p><a href='/favorites'>مشاريعي المحفوظة ⭐</a></p>"
            "<p><a href='/'>العودة للتطبيق</a></p>"
        ))

    def remove_favorite(self, project_id):
        conn = sqlite3.connect("projects.db")
        cur = conn.cursor()

        cur.execute("SELECT id FROM users ORDER BY id DESC LIMIT 1")
        user = cur.fetchone()

        if not user:
            conn.close()
            self.send_html(self.page(
                "<h1>لا يوجد حساب ⚠️</h1>"
                "<p><a href='/register'>إنشاء حساب</a></p>"
            ))
            return

        cur.execute(
            "DELETE FROM favorites WHERE user_id = ? AND project_id = ?",
            (user[0], project_id)
        )

        conn.commit()
        conn.close()

        self.send_html(self.page(
            "<h1>تم حذف المشروع من المفضلة 🗑️</h1>"
            "<p><a href='/favorites'>العودة للمفضلة</a></p>"
        ))

    def get_current_user(self):
        from http.cookies import SimpleCookie

        cookie = SimpleCookie()
        cookie.load(self.headers.get("Cookie", ""))

        if "user_id" not in cookie:
            return None

        try:
            return int(cookie["user_id"].value)
        except ValueError:
            return None

    def redirect(self, path):
        self.send_response(302)
        self.send_header("Location", path)
        self.end_headers()

    def save_favorite(self, project_id):
        conn = sqlite3.connect("projects.db")
        cur = conn.cursor()

        # استخدام آخر مستخدم مسجل حاليًا
        cur.execute("SELECT id FROM users ORDER BY id DESC LIMIT 1")
        user = cur.fetchone()

        if not user:
            conn.close()
            self.send_html(self.page(
                "<h1>⚠️ أنشئ حسابًا أولًا</h1>"
                "<p><a href='/register'>إنشاء حساب</a></p>"
            ))
            return

        try:
            cur.execute(
                "INSERT INTO favorites (user_id, project_id) VALUES (?, ?)",
                (user[0], project_id)
            )
            conn.commit()
            message = "تم حفظ المشروع في المفضلة ⭐"
        except sqlite3.IntegrityError:
            message = "المشروع محفوظ بالفعل ⭐"

        conn.close()

        self.send_html(self.page(
            f"<h1>{message}</h1>"
            "<p><a href='/'>العودة للتطبيق</a></p>"
        ))

    def do_POST(self):
        if self.path == "/login":
            length = int(self.headers.get("Content-Length", 0))
            data = self.rfile.read(length).decode("utf-8")
            form = parse_qs(data)

            phone = form.get("phone", [""])[0].strip()

            conn = sqlite3.connect("projects.db")
            cur = conn.cursor()

            cur.execute(
                "SELECT id, name FROM users WHERE phone = ?",
                (phone,)
            )

            user = cur.fetchone()
            conn.close()

            if not user:
                self.send_html(self.page(
                    "<h1>الحساب غير موجود ❌</h1>"
                    "<p><a href='/register'>إنشاء حساب جديد</a></p>"
                ))
                return

            self.send_response(302)
            self.send_header(
                "Set-Cookie",
                f"user_id={user[0]}; Path=/"
            )
            self.send_header("Location", "/")
            self.end_headers()
            return

        if self.path == "/favorite":
            length = int(self.headers.get("Content-Length", 0))
            data = self.rfile.read(length).decode("utf-8")
            form = parse_qs(data)

            project_id = int(form.get("project_id", ["0"])[0])
            self.save_favorite(project_id)
            return

        if self.path == "/remove_favorite":
            length = int(self.headers.get("Content-Length", 0))
            data = self.rfile.read(length).decode("utf-8")
            form = parse_qs(data)

            project_id = int(form.get("project_id", ["0"])[0])
            self.remove_favorite(project_id)
            return

        if self.path == "/register":
            length = int(self.headers.get("Content-Length", 0))
            data = self.rfile.read(length).decode("utf-8")
            form = parse_qs(data)

            name = form.get("name", [""])[0].strip()
            phone = form.get("phone", [""])[0].strip()

            if name and phone:
                self.register_user(name, phone)
            else:
                self.send_html(self.page(
                    "<h1>البيانات ناقصة ⚠️</h1>"
                    "<p><a href='/register'>العودة</a></p>"
                ))
            return

        length = int(self.headers.get("Content-Length", 0))
        data = self.rfile.read(length).decode("utf-8")
        form = parse_qs(data)

        capital = int(form.get("capital", ["0"])[0])
        hours = int(form.get("hours", ["0"])[0])
        category = form.get("category", ["all"])[0]

        conn = sqlite3.connect("projects.db")
        cursor = conn.cursor()

        if category == "all":
            cursor.execute("""
            SELECT id, name, category, startup_cost,
                   monthly_cost, expected_revenue, description, effort, requirements
            FROM projects
            WHERE min_capital <= ?
            ORDER BY min_capital ASC
            """, (capital,))
        else:
            cursor.execute("""
            SELECT id, name, category, startup_cost,
                   monthly_cost, expected_revenue, description, effort, requirements
            FROM projects
            WHERE min_capital <= ? AND category = ?
            ORDER BY min_capital ASC
            """, (capital, category))

        projects = cursor.fetchall()
        conn.close()

        cards = ""

        for p in projects:
            project_id, name, cat, startup, monthly, revenue, description, effort, requirements = p
            profit = revenue - monthly

            # نقطة التعادل التقديرية
            if profit > 0:
                break_even = round(startup / profit, 1)
                break_even_text = f"{break_even} شهر"
            else:
                break_even_text = "غير متاح حاليًا"

            # نسبة المطابقة حسب رأس المال والوقت والجهد
            if startup <= 0:
                capital_score = 100
            else:
                capital_ratio = capital / startup
                capital_score = round(min(100, capital_ratio * 70))

            if hours >= 8:
                time_score = 100
            elif hours >= 6:
                time_score = 85
            elif hours >= 4:
                time_score = 70
            elif hours >= 2:
                time_score = 50
            else:
                time_score = 30

            # درجة الجهد محفوظة لكل مشروع في قاعدة البيانات
            effort = effort if "effort" in locals() else 3
            effort_score = max(0, min(100, 100 - ((effort - 1) * 15)))

            score = round(
                (capital_score * 0.40) +
                (time_score * 0.30) +
                (effort_score * 0.30)
            )

            score = max(0, min(100, score))

            cards += f"""<p>🎯 نسبة المطابقة: {score}%</p>
            <div class="card">
            <h2><a href="/project/{project_id}">{name}</a></h2>
            <p>📂 المجال: {cat}</p>
            <p>💰 تكلفة البداية: {startup} ريال</p>
            <p>📈 الإيراد المتوقع: {revenue} ريال شهرياً</p>
            <p>💵 الربح التقديري: {profit} ريال شهرياً</p>
            <p>⏳ نقطة التعادل التقديرية: {break_even_text}</p>
            <p>🧰 المتطلبات: {requirements}</p>
            <p>📝 خطوات البدء: تجهيز المتطلبات → تحديد الموردين → إطلاق المشروع → التسويق → متابعة النتائج</p>
            <form method="POST" action="/favorite">
                <input type="hidden" name="project_id" value="{project_id}">
                <button type="submit">⭐ حفظ المشروع</button>
            </form>
            <p>{description}</p>
            </div>
            """

        if not cards:
            cards = "<p>لا توجد مشاريع مطابقة لرأس المال والمجال المحددين.</p>"

        content = f"""
        <h1>النتائج 🔎</h1>
        {cards}
        <br>
        <a href="/">← بحث جديد</a>
        """

        self.send_html(self.page(content))

import os

PORT = int(os.environ.get("PORT", 9090))
server = HTTPServer(("0.0.0.0", PORT), Handler)
print("Server running on http://127.0.0.1:9090")
server.serve_forever()
