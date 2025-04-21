import json
import pandas as pd
import matplotlib.pyplot as plt

# If you want to export the table as a PNG using dataframe_image, install it:
# pip install dataframe_image
# Then uncomment the dataframe_image import and use it at the end.

# import dataframe_image as dfi


def main():
    # 1. Load the JSON data
    with open("resource_usage_summary.json", "r") as file:
        data = json.load(file)

    # 2. Prepare data for bar charts
    chart_data = []
    for user, user_info in data.items():
        summary = user_info["summary"]
        chart_data.append(
            {
                "name": user,
                "totalCost": summary["totalCost"],
                "totalGPUs": summary["totalGPUs"],
                "numberOfMachines": summary["numberOfMachines"],
                "totalGPUhours": summary["totalGpuHours"],
                "totalCostPerDay": summary["totalCostPerHour"] * 24,
            }
        )

    df_charts = pd.DataFrame(chart_data)

    df_sorted = df_charts.sort_values(by="totalCostPerDay", ascending=False)
    plt.bar(df_sorted["name"], df_sorted["totalCostPerDay"])
    plt.xticks(rotation=45)
    plt.title("Cost of GPU usage per Day by User (in dollars)")
    plt.tight_layout()
    plt.savefig("bar_totalCostPerDay.png")
    plt.close()

    # 2.a) Bar chart: name vs totalCost, descending
    df_sorted = df_charts.sort_values(by="totalCost", ascending=False)
    plt.bar(df_sorted["name"], df_sorted["totalCost"])
    plt.xticks(rotation=45)
    plt.title("Total Cost by User (in dollars)")
    plt.tight_layout()
    plt.savefig("bar_totalCost.png")
    plt.close()

    # 2.b) Bar chart: name vs totalGPUs, descending
    df_sorted = df_charts.sort_values(by="totalGPUs", ascending=False)
    plt.bar(df_sorted["name"], df_sorted["totalGPUs"])
    plt.xticks(rotation=45)
    plt.title("Total GPUs by User")
    plt.tight_layout()
    plt.savefig("bar_totalGPUs.png")
    plt.close()

    # 2.c) Bar chart: name vs numberOfMachines, descending
    df_sorted = df_charts.sort_values(by="numberOfMachines", ascending=False)
    plt.bar(df_sorted["name"], df_sorted["numberOfMachines"])
    plt.xticks(rotation=45)
    plt.title("Number of Machines by User")
    plt.tight_layout()
    plt.savefig("bar_numMachines.png")
    plt.close()

    # 2.d) Bar chart: name vs totalGPUhours, descending
    df_sorted = df_charts.sort_values(by="totalGPUhours", ascending=False)
    plt.bar(df_sorted["name"], df_sorted["totalGPUhours"])
    plt.xticks(rotation=45)
    plt.title("Total GPU Hours by User")
    plt.tight_layout()
    plt.savefig("bar_totalGPUhours.png")
    plt.close()

    # 3. Create table with columns: [username, instance name, running_time]
    table_data = []
    for user, user_info in data.items():
        for machine in user_info["machines"]:
            table_data.append(
                {
                    "username": user,
                    "instance_name": machine["name"],
                    "running_time (in hours)": machine["totalHours"],
                }
            )

    df_table = pd.DataFrame(table_data)
    df_table_sorted = df_table.sort_values(
        by="running_time (in hours)", ascending=False
    )

    # Option A: Save table as PNG using a matplotlib table
    fig, ax = plt.subplots(figsize=(8, 0.5 + 0.3 * len(df_table_sorted)))
    ax.axis("off")
    # Build a list of lists for table display
    table_list = [df_table_sorted.columns.to_list()] + df_table_sorted.values.tolist()
    the_table = ax.table(
        cellText=table_list, colLabels=None, cellLoc="center", loc="center"
    )
    the_table.auto_set_font_size(False)
    the_table.set_fontsize(8)
    the_table.scale(1, 1.2)  # Adjust scale as needed
    plt.savefig("table.png", bbox_inches="tight")
    plt.close()

    # Option B: Use dataframe_image (requires "pip install dataframe_image")
    # dfi.export(df_table_sorted, "table.png")


if __name__ == "__main__":
    main()
