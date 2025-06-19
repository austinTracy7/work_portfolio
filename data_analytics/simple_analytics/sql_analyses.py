import sqlite3

import matplotlib.pyplot as plt
import pandas as pd

db_path = "data/burgers_and_shakeland.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Question 1
# What is the most popular item at Burgers and Shakeland?
cursor.execute("""
    SELECT Item
    FROM burgers_and_shakeland
    GROUP BY Item
    ORDER BY COUNT(*) DESC
    LIMIT 1
""")
most_popular_item = cursor.fetchone()[0]

# Question 1 Output
print(f"The most popular item is a {most_popular_item}")

# Question 2
# Which location is the busiest? Does the answer to this question change throughout the day?
cursor.execute("""
    SELECT Location
    FROM burgers_and_shakeland
    GROUP BY Location
    ORDER BY COUNT(*) DESC
    LIMIT 1
""")
busiest_location = cursor.fetchone()[0]

hourly_counts = pd.read_sql("""
    WITH ITEMS_BY_HOUR AS ( 
        SELECT Location, SUBSTR(DateTime,12,2) AS HOUR, COUNT(*) AS ITEMS_SOLD
        FROM burgers_and_shakeland
        GROUP BY Location, SUBSTR(DateTime,12,2)
        ORDER BY SUBSTR(DateTime,12,2)
    ),
    MAXIMUM_VALUES_BY_HOUR AS (
        SELECT HOUR, MAX(ITEMS_SOLD) AS ITEMS_SOLD
        FROM ITEMS_BY_HOUR
        GROUP BY HOUR
    )
    SELECT I.Hour, I.Location 
    FROM MAXIMUM_VALUES_BY_HOUR AS M
    LEFT JOIN ITEMS_BY_HOUR AS I ON M.ITEMS_SOLD = I.ITEMS_SOLD 
""")

busiest_per_hour = hourly_counts.idxmax(axis=1)
busiest_per_hour_list = list(busiest_per_hour.to_dict().items())
len_business_per_hour_list = len(busiest_per_hour_list) # to not recompute again and again

summarized_busiest_hours = busiest_per_hour_list[0:1] + [
        pair for i, pair in enumerate(busiest_per_hour_list[1:-1]) if (pair[1] != busiest_per_hour_list[i][1]) or (pair[1] != busiest_per_hour_list[i+2][1])
    ] + busiest_per_hour_list[-1:]
summarized_busiest_hours_str = "\n".join([f"{x[0][0]}-{x[1][0]} {x[0][1]}" for x in list(zip(summarized_busiest_hours[::2], summarized_busiest_hours[1::2]))])

# Plotting
plt.figure(figsize=(12, 6))
hourly_counts.plot(kind='line', marker='o', ax=plt.gca())

plt.title("Transaction Volume by Location Throughout the Day")
plt.xlabel("Hour of the Day")
plt.ylabel("Number of Transactions")
plt.legend(title="Location")
plt.grid(True)
plt.xticks(range(0, 24))  # Ensure all hours are visible

# Question 2 Output
print(f"The busiest location overall is: {busiest_location}")
plt.show()
print(f"The busiest location by hour break down:\n {summarized_busiest_hours_str}")

# Question 3
# A combo meal consists of 1 Burger, 1 Fry, and either a drink or a shake (not both). How many Combo meals were sold from the State Street location in April?
total_april_possible_state_street_combos = pd.read_sql("""
    WITH STATE_STREET_APRIL_ORDERS AS (
        SELECT *, CASE WHEN ItemID = 4 THEN 3 ELSE ItemID END AS ItemCategory FROM burgers_and_shakeland
        WHERE Location = 'State Street' AND SUBSTR(DateTime,6,2) = '04'
    ),
    CATEGORIZED_ELEMENTS AS (
        SELECT DateTime, Location, Transaction_EmployeeID, ItemCategory, COUNT(*) AS Items_Sold FROM STATE_STREET_APRIL_ORDERS
        GROUP BY DateTime, Location, ItemCategory, Transaction_EmployeeID
    ),
    COMBOS AS (
        SELECT MIN(Items_Sold) AS Items_Sold, COUNT(*) > 2 AS IS_COMBO FROM CATEGORIZED_ELEMENTS
        GROUP BY DateTime, Location, Transaction_EmployeeID
    )
    SELECT SUM(Items_Sold)
        FROM COMBOS
        WHERE IS_COMBO = 1
    """,conn).iloc[0].iloc[0]

# Question 3 Output
print(f"The number of combo meals sold from the State Street location in April is {total_april_possible_state_street_combos}.")

# Question 4
# Some of the employees have been complaining about working long hours. Based only on the transaction data, can you tell if any employees are working more than a typical 8-hour shift?
long_days_df  = pd.read_sql("""
    WITH ORDER_TIMES AS ( 
        SELECT Transaction_EmployeeID, Employee_Name, SUBSTR(DateTime,1,INSTR(DateTime, ' ') - 1) AS Date, SUBSTR(DateTime,INSTR(DateTime, ' ') + 1) AS Time
        FROM burgers_and_shakeland
    ),
    MINUTES_AFTER_MIDIGHT AS (
        SELECT Transaction_EmployeeID, Employee_Name, Date, SUBSTR(Time,1,INSTR(Time, ':') - 1) * 60 + SUBSTR(SUBSTR(Time,INSTR(Time, ':') + 1),1,2) AS MINUTES_SINCE_MIDNIGHT
        FROM ORDER_TIMES
    ),
    LENGTH_OF_DAY AS (
        SELECT Transaction_EmployeeID, Employee_Name, Date, MAX(MINUTES_SINCE_MIDNIGHT) - MIN(MINUTES_SINCE_MIDNIGHT) AS TOTAL_MINUTES FROM MINUTES_AFTER_MIDIGHT
            GROUP BY Transaction_EmployeeID, Employee_Name, Date
    ),
    LONG_DAYS_BY_EMPLOYEE AS (
        SELECT Transaction_EmployeeID, Employee_Name, Date, ROUND(TOTAL_MINUTES / 60.0, 2) AS LONG_DAY_TIME FROM LENGTH_OF_DAY
            WHERE TOTAL_MINUTES > 540
    )
    SELECT LONG_DAY_TIME, COUNT(*) AS INSTANCES
        FROM LONG_DAYS_BY_EMPLOYEE
        GROUP BY LONG_DAY_TIME
        ORDER BY LONG_DAY_TIME
""",conn)

more_than_eight_count, more_than_nine_count, highest_demand_hours, shortest_break = pd.read_sql("""
    WITH ORDER_TIMES AS ( 
        SELECT Transaction_EmployeeID, Employee_Name, SUBSTR(DateTime,1,INSTR(DateTime, ' ') - 1) AS Date, SUBSTR(DateTime,INSTR(DateTime, ' ') + 1) AS Time
        FROM burgers_and_shakeland
    ),
    MINUTES_AFTER_MIDIGHT AS (
        SELECT Transaction_EmployeeID, Employee_Name, Date, SUBSTR(Time,1,INSTR(Time, ':') - 1) * 60 + SUBSTR(SUBSTR(Time,INSTR(Time, ':') + 1),1,2) AS MINUTES_SINCE_MIDNIGHT
        FROM ORDER_TIMES
    ),
    POSSIBLE_BREAKS AS (
        SELECT Transaction_EmployeeID, Employee_Name, Date, MINUTES_SINCE_MIDNIGHT,
                MINUTES_SINCE_MIDNIGHT - LAG(MINUTES_SINCE_MIDNIGHT) OVER(PARTITION BY Transaction_EmployeeID, Date) AS Possible_Break_Time 
        FROM MINUTES_AFTER_MIDIGHT
    ),
    TRUE_BREAK_POTENTIAL AS (
        SELECT *, CASE WHEN Possible_Break_Time > 15 THEN Possible_Break_Time ELSE 0 END AS Longer_Possible_Break FROM POSSIBLE_BREAKS
    ),
    GROUPED_DATA AS (
        SELECT Transaction_EmployeeID, Employee_Name, Date, MAX(Possible_Break_Time) AS LONGEST_BREAK, MAX(MINUTES_SINCE_MIDNIGHT) - MIN(MINUTES_SINCE_MIDNIGHT) AS TOTAL_MINUTES, SUM(Longer_Possible_Break) AS POSSIBLE_DOWN_TIME FROM TRUE_BREAK_POTENTIAL
        GROUP BY Transaction_EmployeeID, Employee_Name, Date
    ),
    LONG_DAY_COUNT AS (
        SELECT COUNT(*) AS VALUE FROM GROUPED_DATA
            WHERE TOTAL_MINUTES > 480
    ),
    LONGER_DAY_COUNT AS (
        SELECT COUNT(*) AS VALUE FROM GROUPED_DATA
            WHERE TOTAL_MINUTES > 540
    ),
    LONGEST_UNINTERUPTED_DAY AS (
        SELECT MAX(TOTAL_MINUTES - POSSIBLE_DOWN_TIME)/60 FROM GROUPED_DATA
            WHERE TOTAL_MINUTES > 480
    ),
    SHORTEST_BREAK AS (
        SELECT MIN(LONGEST_BREAK) FROM GROUPED_DATA
            WHERE TOTAL_MINUTES > 480
    )
    SELECT * FROM LONG_DAY_COUNT
        UNION ALL
    SELECT * FROM LONGER_DAY_COUNT
        UNION ALL
    SELECT * FROM LONGEST_UNINTERUPTED_DAY
        UNION ALL
    SELECT * FROM SHORTEST_BREAK
    
""",conn)["VALUE"].to_list()

# Question 4 Output
output = ""
if more_than_eight_count > 0:
    output += f"""There are {more_than_eight_count} shifts that were over 8 hours. (The word shifts is used here to refer to the time between a worker starting and ending in a given day not necessarily the specific time within that day on the clock.)"""
    if more_than_nine_count > 0:
        output +=  f""" More importantly, of these {more_than_nine_count} were longer than 9 hours (which would be longer than an eight hour shift with a full hour lunch or would require returning to work). This breaks down by shift length as follows:\n""" + "\n".join([f"{x[0]} hours-{x[1]} instances" for x in long_days_df.to_records(index=False)]) + "\n"

    if highest_demand_hours > 8:
        output += f" Most importantly, there was an instance in the data that required {highest_demand_hours} hours of what can be assumed to be continual work."
    else:
        output += f" There is potential room for investigation of if that time is well spent for all involved with only {highest_demand_hours} being continual work."
    if shortest_break < 60:
        output += f"Some individuals have worked eight hour plus hour shifts without more than {shortest_break} minutes between transactions."
else:
    output = "There is no evidence in the transactional data for any shifts even possibly be longer than 8 hours."
print(output)