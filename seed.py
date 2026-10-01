from database import create_database, add_project

create_database()

projects = [
    {
        "name": "متجر إلكتروني متخصص",
        "category": "تجارة إلكترونية",
        "min_capital": 3000,
        "startup_cost": 2000,
        "monthly_cost": 500,
        "expected_revenue": 2000,
        "description": "متجر متخصص في منتج أو فئة منتجات محددة.",
        "steps": "اختيار المنتج، دراسة المنافسين، إنشاء المتجر، التسويق، متابعة المبيعات"
    },
    {
        "name": "خدمة تصميم وإدارة حسابات",
        "category": "خدمات رقمية",
        "min_capital": 1000,
        "startup_cost": 500,
        "monthly_cost": 200,
        "expected_revenue": 1500,
        "description": "تقديم خدمات تصميم محتوى وإدارة حسابات للشركات الصغيرة.",
        "steps": "تجهيز نماذج أعمال، تحديد الخدمات، إنشاء باقات، البحث عن العملاء"
    },
    {
        "name": "مشروع طباعة حسب الطلب",
        "category": "تجارة",
        "min_capital": 5000,
        "startup_cost": 3500,
        "monthly_cost": 700,
        "expected_revenue": 3000,
        "description": "بيع منتجات مطبوعة حسب طلب العميل.",
        "steps": "اختيار المنتجات، تجهيز التصاميم، اختيار مورد، إنشاء المتجر، التسويق"
    },
    {
        "name": "خدمة تنظيف متنقلة",
        "category": "خدمات",
        "min_capital": 8000,
        "startup_cost": 6000,
        "monthly_cost": 1200,
        "expected_revenue": 5000,
        "description": "خدمة تنظيف متنقلة للمنازل أو المنشآت حسب نطاق الخدمة.",
        "steps": "تحديد الخدمة، شراء المعدات، التراخيص اللازمة، التسويق، استقبال الحجوزات"
    }
]

for project in projects:
    add_project(
        project["name"],
        project["category"],
        project["min_capital"],
        project["startup_cost"],
        project["monthly_cost"],
        project["expected_revenue"],
        project["description"],
        project["steps"]
    )

print("تمت إضافة المشاريع ✅")

