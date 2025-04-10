```
       .---.        .-----------
      /     \  __  /    ------
     / /     \(  )/    -----
    //////   ' \/ `   ---
   //// / // :    : ---
  // /   /  /`    '--
 //          //..\\
        ====UU====UU====
            '//||\\`
              ''``
   RUNPOD OBSERVATORY
```

# RunPod Observatory

A tool to monitor and analyze your RunPod usage.

## Installation

Install the required package:

```bash
pip install dataframe_image
```

Make sure you have the `RUNPOD_API_KEY` environment variable set up. You can find your API key in the [RunPod user settings](https://www.runpod.io/console/user/settings).

## Execution

Run the analysis script:

```bash
sh analyse_runpod.sh
```

### Setting Up as a Cron Job

To automatically run the analysis every 3 hours:

1. Open your crontab configuration:
   ```bash
   crontab -e
   ```

2. Add the following line to the editor:
   ```
   0 */3 * * * /path/to/analyse_runpod.sh
   ```
   This tells cron to run `analyse_runpod.sh` every 3 hours (00:00, 03:00, 06:00, etc.)

3. Save and exit the editor. The cron job is now active.

## About

RunPod Observatory helps you keep track of your RunPod resource usage, providing insights to optimize your cloud GPU expenses.
