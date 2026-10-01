import sqlite3

conn = sqlite3.connect("projects.db")
cursor = conn.cursor()

capital = int(input("Capital: "))

cursor.execute("""
SELECT name, category, min_capital, startup_cost,
       monthly_cost, expected_revenue
FROM projects
WHERE min_capital <= ?
ORDER BY min_capital ASC
""", (capital,))

projects = cursor.fetchall()

print("\nMatching projects:\n")

if not projects:
    print("No projects found.")
else:
    for p in projects:
        name, category, minimum, startup, monthly, revenue = p
        profit = revenue - monthly

        print("Project:", name)
        print("Category:", category)
        print("Minimum capital:", minimum)
        print("Startup cost:", startup)
        print("Monthly cost:", monthly)
        print("Estimated revenue:", revenue)
        print("Estimated monthly profit:", profit)
        print("-" * 30)

conn.close()
