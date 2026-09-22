from src.utilities.db import get_connection

BRANCHES = [
    ("Freedom Plains Branch", "Freedom Plains", "NY", "2015-03-01"),
    ("Manhattan Downtown", "New York", "NY", "2010-06-15"),
    ("Brooklyn Heights", "Brooklyn", "NY", "2018-01-20"),
    ("Poughkeepsie Main", "Poughkeepsie", "NY", "2012-09-10"),
    ("Albany Central", "Albany", "NY", "2020-11-05"),
]

MERCHANTS = [
    ("Whole Foods Market", "grocery", "New York", "USA"),
    ("Shell Gas Station", "fuel", "New York", "USA"),
    ("Best Buy", "electronics", "New York", "USA"),
    ("Delta Airlines", "travel", "New York", "USA"),
    ("Amazon", "online_retail", "Seattle", "USA"),
    ("Uber", "transportation", "San Francisco", "USA"),
    ("Netflix", "subscription", "Los Gatos", "USA"),
    ("Alibaba", "online_retail", "Hangzhou", "China"),
    ("Duty Free Emirates", "travel", "Dubai", "UAE"),
    ("Local Corner Store", "grocery", "Freedom Plains", "USA"),
]


def seed_branches(cur):
    cur.executemany(
        """INSERT INTO branches (branch_name, city, state, opened_date)
           VALUES (%s, %s, %s, %s)""",
        BRANCHES,
    )


def seed_merchants(cur):
    cur.executemany(
        """INSERT INTO merchants (merchant_name, category, city, country)
           VALUES (%s, %s, %s, %s)""",
        MERCHANTS,
    )


def main():
    conn = get_connection()
    cur = conn.cursor()
    seed_branches(cur)
    seed_merchants(cur)
    conn.commit()
    print(f"Inserted {len(BRANCHES)} branches and {len(MERCHANTS)} merchants.")
    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
