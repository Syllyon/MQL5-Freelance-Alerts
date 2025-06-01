
import sqlite3
import datetime
import matplotlib.pyplot as plt
import collections
import re
import os

# --- Database Setup ---
def create_connection_and_table(db_file=":memory:"):
    """ Create a database connection to an in-memory SQLite database and create jobs table """
    conn = None
    try:
        DB_NAME = 'mql5-freelance.db'
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            budget TEXT,
            applications INTEGER,
            date_posted TEXT,
            UNIQUE(title, date_posted)
        )
        """)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    return conn

# --- Data Processing ---
def parse_budget_to_numeric(budget_str):
    """ Parses a budget string into a numeric value. Tries to handle ranges and 'k'. """
    if not isinstance(budget_str, str):
        return None

    text = budget_str.lower()
    text = text.replace(',', '')
    text = re.sub(r'\s*(per hour|per year|/hr|/year|ph|pa|\+.*)\s*', '', text) # Remove units and bonuses
    text = re.sub(r'[$\€\£]', '', text)
    
    # Handle 'k' for thousands, ensuring it's attached to a number
    text = re.sub(r'(\d+\.?\d*)k', lambda m: str(float(m.group(1)) * 1000), text)

    numbers = re.findall(r'\d+\.?\d*', text)
    numeric_values = [float(n) for n in numbers]

    if not numeric_values:
        return None
    if len(numeric_values) >= 2: # e.g. "50000-70000"
        return (numeric_values[0] + numeric_values[1]) / 2.0 
    return numeric_values[0]

def fetch_and_process_data(conn):
    """ Fetches data and processes dates (ISO format) and budgets. """
    cursor = conn.cursor()
    cursor.execute("SELECT date_posted, budget FROM jobs")
    raw_data = cursor.fetchall()

    processed_data = []
    for date_str, budget_str in raw_data:
        try:
            # Updated format string for ISO 8601 with 'Z'
            dt_object = datetime.datetime.strptime(date_str, '%Y-%m-%dT%H:%MZ')
            # If your times are truly UTC and you want to work with them as naive (local)
            # or convert to a specific timezone, you might need further handling here.
            # For now, strptime with 'Z' correctly parses it as a naive datetime in Python 3.6+
            # if the 'Z' is part of the format string.
            # For Python 3.7+ `fromisoformat` is also an option if the string ends with 'Z'
            # dt_object = datetime.datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            # Or, for explicit UTC awareness:
            # dt_object = datetime.datetime.strptime(date_str, '%Y-%m-%dT%H:%MZ')
            # dt_object = dt_object.replace(tzinfo=datetime.timezone.utc) # Make it timezone-aware
            # Then, if needed, convert to local time:
            # dt_object = dt_object.astimezone(None) # Converts to system's local timezone

            numeric_budget = parse_budget_to_numeric(budget_str)
            processed_data.append({
                'datetime': dt_object,
                'weekday': dt_object.strftime('%A'), # Full weekday name
                'hour': dt_object.hour,
                'budget': numeric_budget
            })
        except ValueError as e:
            print(f"Could not parse date string '{date_str}' with format '%Y-%m-%dT%H:%MZ': {e}")
        except Exception as e:
            print(f"Error processing row (date: {date_str}, budget: {budget_str}): {e}")
    return processed_data

# --- Graphing Functions ---
def plot_active_weekdays(data, output_filename="active_weekdays.svg"):
    """ Generates a bar chart of job postings by weekday. """
    if not data:
        print("No data available to plot active weekdays.")
        return
        
    weekday_counts = collections.Counter(item['weekday'] for item in data)
    days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    ordered_counts = [weekday_counts.get(day, 0) for day in days_order]

    plt.figure(figsize=(10, 6))
    plt.bar(days_order, ordered_counts, color='skyblue')
    plt.title('Job Postings by Day of the Week')
    plt.xlabel('Day of the Week')
    plt.ylabel('Number of Job Postings')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_filename)
    plt.close()
    print(f"Graph saved as {output_filename}")

def plot_active_hours(data, output_filename="active_hours.svg"):
    """ Generates a bar chart of job postings by hour of the day. """
    if not data:
        print("No data available to plot active hours.")
        return

    hour_counts = collections.Counter(item['hour'] for item in data)
    hours_order = range(24)

    ordered_counts = [hour_counts.get(hour, 0) for hour in hours_order]
    hour_labels = [f"{h:02d}:00" for h in hours_order]

    plt.figure(figsize=(12, 6))
    plt.bar(hour_labels, ordered_counts, color='lightcoral')
    plt.title('Job Postings by Hour of the Day')
    plt.xlabel('Hour of the Day (UTC)')
    plt.ylabel('Number of Job Postings')
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig(output_filename)
    plt.close()
    print(f"Graph saved as {output_filename}")

def plot_budget_by_hour(data, output_filename="budget_by_hour.svg"):
    """ Generates a bar chart of average budget by hour of the day. """
    if not data:
        print("No data available to plot budget by hour.")
        return

    budgets_by_hour = collections.defaultdict(list)
    for item in data:
        if item['budget'] is not None:
            budgets_by_hour[item['hour']].append(item['budget'])

    hours_order = range(24)
    average_budgets = []
    for hour in hours_order:
        if hour in budgets_by_hour and budgets_by_hour[hour]:
            average_budgets.append(sum(budgets_by_hour[hour]) / len(budgets_by_hour[hour]))
        else:
            average_budgets.append(0)

    hour_labels = [f"{h:02d}:00" for h in hours_order]

    plt.figure(figsize=(12, 6))
    plt.bar(hour_labels, average_budgets, color='lightgreen')
    plt.title('Average Budget by Posting Hour (UTC)')
    plt.xlabel('Hour of the Day (Posting Time - UTC)')
    plt.ylabel('Average Budget')
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig(output_filename)
    plt.close()
    print(f"Graph saved as {output_filename}")

# --- Main Execution ---
if __name__ == "__main__":
    db_conn = create_connection_and_table()

    if db_conn:
        job_data = fetch_and_process_data(db_conn)

        if job_data:
            output_dir = "job_graphs"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            plot_active_weekdays(job_data, os.path.join(output_dir, "active_weekdays.svg"))
            plot_active_hours(job_data, os.path.join(output_dir, "active_hours.svg"))
            plot_budget_by_hour(job_data, os.path.join(output_dir, "budget_by_hour.svg"))
            print(f"\nAll graphs saved in the '{output_dir}' directory.")
        else:
            print("No processed data available to generate graphs.")
        
        db_conn.close()
    else:
        print("Failed to establish database connection.")

