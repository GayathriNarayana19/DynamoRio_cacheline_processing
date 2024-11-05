# Cacheline processing based on DynamoRio experiments

## Steps

1. Once "python3 cache_line_usage.py" has been run, it will prompt for the "name and path for input log or txt file" you generated using dynamoRio. Pass that as input. The script continues to prompt the user for entering names for two output CSV files. Frst CSV gives a detailed first level overview of the trace and second CSV provides the used and unused % ranges for underutilized cachelines. Name as per your preferences. The script will also generate an image of cacheline distribution. 


## Example Usage:

```bash
python3 cache_line_usage.py 

Name and path to the input log / txt file: ../instrace.odp_sched_perf.610841.0001.log
Provide a Path/name to save the first level detailed output CSV file: /Users/gayyeg01/Downloads/Dynamo_output/Detailed_Trace.csv
Provide a Path/name to save the unused cacheline percentage CSV file: /Users/gayyeg01/Downloads/Dynamo_output/Underutilization_view.csv
```
```bash
Processing complete. Results written to /Users/gayyeg01/Downloads/Dynamo_output/Detailed_Trace.csv
Processed cacheline data and written to /Users/gayyeg01/Downloads/Dynamo_output/Underutilization_view.csv and image is saved to /Users/gayyeg01/Downloads/Dynamo_output/Underutilization_view_cacheline_distribution.png
```

2. Run the optimization_hotspots.py as follows. Pass the inputs when prompted. Provide the first level detailed output CSV file you generated from the cache_line_usage.py script as input and pass an output name for the second level csv. This second level csv basically shows the hotspots/potential cachelines to begin optimization.  
Note: For the prompt "Enter the number of top cachelines to process (-1 for all)", enter -1 if you want to view all cachelines. Or if you want to enter top 10 or 50 hotspots/potential cachelines, enter that number instead. 

### Example Usage:
```bash
python3 optimization_hotspots.py

Name and path of the first level CSV file: /Users/gayyeg01/Downloads/Dynamo_output/Detailed_Trace.csv
Provide a name to save the second level output CSV file : /Users/gayyeg01/Downloads/Dynamo_output/hotspot_second_level.csv
Enter the number of top cachelines to process (-1 for all): -1
```
```bash
Processing complete. Sorted cacheline data written to /Users/gayyeg01/Downloads/Dynamo_output/hotspot_second_level.csv
```
