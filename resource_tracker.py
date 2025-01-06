import psutil  # Library for system resource monitoring
from tabulate import tabulate  # Library for formatting tabular data
import smtplib  # Library for sending emails
from email.mime.text import MIMEText
import time  # Library for adding delays

# Threshold for resource usage (e.g., 85% for CPU, memory, or disk usage)
USAGE_THRESHOLD = 85

# Flags to track if an email has already been sent for each resource
alert_sent = {"CPU": False, "Memory": False, "Disk": False}

# Function to get current system resource usage
def get_system_usage():
    """
    Retrieve the current CPU, memory, and disk usage of the system.

    Returns:
        list: A list of resource usage data including CPU, memory, and disk usage percentages.
    """
    data = [
        ["CPU", psutil.cpu_percent(interval=1)],
        ["Memory", psutil.virtual_memory().percent],
        ["Disk", psutil.disk_usage('/').percent],
    ]
    return data

# Function to identify the top 3 resource-consuming processes
def get_top_processes():
    """
    Retrieve information about the top 3 processes consuming the most resources.

    Returns:
        list: A list of lists containing process information such as PID, name, CPU usage, and memory usage.
    """
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        processes.append(proc.info)
    top_processes = sorted(processes, key=lambda x: x['cpu_percent'] + x['memory_percent'], reverse=True)[:3]
    return [[p['pid'], p['name'], p['cpu_percent'], p['memory_percent']] for p in top_processes]

# Function to send a notification email when resource usage exceeds the threshold
def send_email(resource, usage, processes):
    """
    Send an email notification when high resource usage is detected.

    Args:
        resource (str): The resource type (e.g., "CPU", "Memory", "Disk").
        usage (float): The percentage usage of the resource.
        processes (list): A list of top processes contributing to high resource usage.
    """
    # Sender and recipient email addresses
    sender = "aws.xxxx@gmail.com"
    recipient = "aws.xxxx@gmail.com"

    # Email subject
    subject = f"Alert: High {resource} Usage Detected!"

    # Format the top processes as a plain-text table
    process_table = "PID    Name                 CPU %    Memory %\n"
    process_table += "-" * 50 + "\n"
    for proc in processes:
        process_table += f"{str(proc[0]).ljust(6)} {proc[1][:20].ljust(20)} {str(proc[2]).ljust(8)} {str(proc[3]).ljust(8)}\n"

    # Email body
    body = f"""
    High {resource} usage detected:
    {resource} Usage: {usage}%

    Top 3 Processes:
    {process_table}
    """

    # Create the email message
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient

    # Send the email using an SMTP server
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender, "udqs xxxx xxxx alat")
            server.send_message(msg)
        print(f"Notification email sent successfully for high {resource} usage.")
    except Exception as e:
        print(f"Failed to send email: {e}")


# Main function to monitor resource usage
if __name__ == "__main__":
    while True:
        usage = get_system_usage()
        print(tabulate(usage, headers=["Resource", "Usage"], tablefmt="grid"))

        for resource, usage_value in usage:
            if usage_value > USAGE_THRESHOLD and not alert_sent[resource]:
                print(f"High {resource} usage detected: {usage_value}%")
                top_processes = get_top_processes()
                send_email(resource, usage_value, top_processes)
                alert_sent[resource] = True  # Mark alert as sent for this resource
            elif usage_value <= USAGE_THRESHOLD:
                alert_sent[resource] = False  # Reset flag if usage goes below threshold

        # Wait for 60 seconds before checking again
        time.sleep(60)
