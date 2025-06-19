import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv(r"data\burgers_and_shakeland.csv")

# Question 1
# What is the most popular item at Burgers and Shakeland?
most_popular_item = df['Item'].value_counts().idxmax()

# Question 1 Output
print(f"The most popular item is a {most_popular_item}")

# Question 2
# Which location is the busiest? Does the answer to this question change throughout the day?
df['DateTime'] = pd.to_datetime(df['DateTime'])
df['Hour'] = df['DateTime'].dt.hour

# Computations
busiest_location = df['Location'].value_counts().idxmax()
hourly_counts = df.groupby(['Hour', 'Location']).size().unstack()
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
to_group_df = df[["DateTime","Location","Transaction EmployeeID","ItemID"]]
to_group_df["ComboCategories"] = to_group_df["ItemID"].apply(lambda x: {1: 1, 2: 2, 3: 3, 4: 3}[x]) # Combine drinks into one category
grouped_drinks_df = to_group_df.groupby(["DateTime","Location","Transaction EmployeeID","ComboCategories"]).count().reset_index()
possible_combo_counts_df = grouped_drinks_df.groupby(["DateTime","Location","Transaction EmployeeID"]).agg({"ComboCategories": "count", "ItemID": "min"}).reset_index() # ItemID is just a count
total_april_possible_state_street_combos = possible_combo_counts_df.loc[(possible_combo_counts_df["ComboCategories"] == 3) & (possible_combo_counts_df["DateTime"].dt.month == 4) & (possible_combo_counts_df["Location"] == "State Street")]["ItemID"].sum()

# Question 3 Output
print(f"The number of combo meals sold from the State Street location in April is {total_april_possible_state_street_combos}.")

# Question 4
# Some of the employees have been complaining about working long hours. Based only on the transaction data, can you tell if any employees are working more than a typical 8-hour shift?

# Note the data has a weird granularity (only 15 minute increments)
df["Date"] = df["DateTime"].dt.date

shifts_df = df.sort_values(["Employee Name","DateTime"])
shifts_df["Break"] = shifts_df.groupby(["Employee Name","Date"])["DateTime"].diff()
shifts_df["Longer_Break"] = shifts_df["Break"].apply(lambda x: 0 if str(x) == "NaT" else x.seconds if x.seconds//60 > 15 else 0)

employee_day_df = shifts_df.groupby(["Transaction EmployeeID", "Employee Name", "Date"]).agg({
        "DateTime": ["min", "max"], "Break": "max", "Longer_Break": ["sum",lambda x: (x != 0).sum()]
    })
employee_day_df["total_seconds_within_workday"] = employee_day_df.apply(lambda row: (row[('DateTime','max')] - row[('DateTime','min')]).seconds, axis=1)
employee_day_df["total_hours_within_workday"] = employee_day_df["total_seconds_within_workday"] / 60 /60
employee_day_df["average_longer_break"] = 0
employee_day_df.loc[(employee_day_df[("Longer_Break","<lambda_0>")] != 0),"average_longer_break"] = employee_day_df.loc[(employee_day_df[("Longer_Break","<lambda_0>")] != 0)].apply(lambda row: row[("Longer_Break","sum")]/row[("Longer_Break","<lambda_0>")] ,axis=1)

# Finding longest days
possible_eight_hour_plus_shifts_df = employee_day_df.loc[employee_day_df["total_hours_within_workday"] > 8.0]
long_days_df = employee_day_df.loc[employee_day_df["total_hours_within_workday"] > 9.0]

# Evaluating time usage
possible_eight_hour_plus_shifts_df["good_working_time"] = possible_eight_hour_plus_shifts_df.apply(lambda row: row[("total_seconds_within_workday","")] - row[("Longer_Break","sum")],axis=1)
highest_demand_hours = possible_eight_hour_plus_shifts_df["good_working_time"].max()/60/60
for shortest_break_i in range(1,int(24*60/15)):
    hardest_eight_hour_shifts = possible_eight_hour_plus_shifts_df[possible_eight_hour_plus_shifts_df[("Break","max")].apply(lambda x: x.seconds == (60 * 15 * shortest_break_i))]
    if not hardest_eight_hour_shifts.empty:
        break

# Question 4 Output
output = ""
if len(possible_eight_hour_plus_shifts_df) > 0:
    output += f"""There are {len(possible_eight_hour_plus_shifts_df)} shifts that were over 8 hours. (The word shifts is used here to refer to the time between a worker starting and ending in a given day not necessarily the specific time within that day on the clock.)"""
    if len(long_days_df) > 0:
        output +=  f""" More importantly, of these {len(long_days_df)} were longer than 9 hours (which would be longer than an eight hour shift with a full hour lunch or would require returning to work). This breaks down by shift length as follows:\n""" + "\n".join([f"{x[0]} hours-{x[1]} instances" for x in pd.DataFrame(long_days_df[[("total_hours_within_workday","")]].value_counts()).reset_index().sort_values([("total_hours_within_workday","")]).set_index([("total_hours_within_workday","")]).to_records()]) + "\n"

    if highest_demand_hours > 8:
        output += f" Most importantly, there was an instance in the data that required {highest_demand_hours} hours of what can be assumed to be continual work."
    else:
        output += f" There is potential room for investigation of if that time is well spent for all involved with only {highest_demand_hours} being continual work."
    if shortest_break_i < 4:
        output += f"Some individuals have worked eight hour plus hour shifts without more than {shortest_break_i * 15} minutes between transactions."
else:
    output = "There is no evidence in the transactional data for any shifts even possibly be longer than 8 hours."
print(output)