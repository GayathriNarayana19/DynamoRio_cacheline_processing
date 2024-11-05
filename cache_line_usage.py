# MIT License
# Copyright (c) 2024  GayathriNarayana19
# Permission is hereby granted to use, copy, modify, and distribute this software.

import csv
import os
import matplotlib.pyplot as plt  

CACHE_LINE_SIZE = 64

def calculate_percentage(used, unused):
    total = used + unused
    if total == 0:  #handle div by 0
        return 0, 0
    used_percentage = (used / total) * 100
    unused_percentage = (unused / total) * 100
    return used_percentage, unused_percentage

def get_percentage_range(percentage):
    if 1 <= percentage < 10:
        return '1.0-10.0'
    elif 10 <= percentage < 20:
        return '10.0-20.0'
    elif 20 <= percentage < 30:
        return '20.0-30.0'
    elif 30 <= percentage < 40:
        return '30.0-40.0'
    elif 40 <= percentage < 50:
        return '40.0-50.0'
    elif 50 <= percentage < 60:
        return '50.0-60.0'
    elif 60 <= percentage < 70:
        return '60.0-70.0'
    elif 70 <= percentage < 80:
        return '70.0-80.0'
    elif 80 <= percentage < 90:
        return '80.0-90.0'
    elif 90 <= percentage <= 100:
        return '90.0-100.0'
    else:
        return None 

#graph based on unused byte percentages & cacheline data
def process_cacheline_data(input_csv, output_csv, show_graph=False):
    cacheline_data = {}
    percentage_ranges = {}
    with open(input_csv, 'r') as infile:
        reader = csv.reader(infile)
        header = next(reader)  #Skipping the header

        for row in reader:
            cache_line = row[1]
            used_bytes = int(row[3])  
            unused_bytes = int(row[4])  #Unused bytes from column E (index 4)

            #Calculate the percentages
            used_percentage, unused_percentage = calculate_percentage(used_bytes, unused_bytes)
            if unused_percentage == 0:
                continue
            #populate the dict
            if cache_line not in cacheline_data:
                cacheline_data[cache_line] = {
                    'cache_line': cache_line,
                    'used_percentage': used_percentage,
                    'unused_percentage': unused_percentage
                }

            #Group cachelines based on their unused percentage ranges
            range_key = get_percentage_range(unused_percentage)
            if range_key not in percentage_ranges:
                percentage_ranges[range_key] = []

            if cache_line not in percentage_ranges[range_key]:
                percentage_ranges[range_key].append(cache_line)

    with open(output_csv, 'w', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(['Cache Line', 'Used Percentage', 'Unused Percentage', 'Range'])

        for range_key, cachelines in percentage_ranges.items():
            for cache_line in cachelines:
                data = cacheline_data[cache_line]
                writer.writerow([
                    data['cache_line'],
                    data['used_percentage'],
                    data['unused_percentage'],
                    range_key
                ])

    print(f"Processed cacheline data and written to {output_csv} and image is saved to {image_name}")

    #Unused percentage range graph
    if show_graph:
        plt.figure(figsize=(10, 6))
        ranges = list(percentage_ranges.keys())
        values = [len(v) for v in percentage_ranges.values()]

        #plt.hist(unused_percentage, bins=10, range=(1, 100), color='blue', edgecolor='black')
        plt.bar(ranges, values, color='red')
        plt.title('Unused Cacheline Percentage Distribution')
        plt.xlabel('Unused Byte Percentage Ranges')
        plt.ylabel('Number of Cachelines')
        plt.xticks(rotation=45)
        plt.gca().yaxis.set_major_locator(plt.MaxNLocator(integer=True))  #integer ticks
        plt.grid(True, axis='y', linestyle='--', alpha=0.7)  #light grid
        plt.ylim(0, max(values) + 1)  
        plt.tight_layout()
        plt.savefig(image_name)
        #plt.show()

#Gets the cache line number based on an input memory addr
def get_cache_line(address):
    return address // CACHE_LINE_SIZE

#Filtering the mem addr values 
def filter_mem_addr(input_file, mem_addr_hits):
    with open(input_file, 'r') as file:
        for line in file:
            parts = line.strip().split(',')
            if len(parts) >= 6 and parts[2] == '1': #Filters the lines that have 1 in is_memory column, ie., col 2
                try:
                    inst_addr = int(parts[0], 16)  #Converts inst addr to an integer for processing
                    mem_addr = int(parts[4], 16)  
                    size = int(parts[5])  
                    exe_name = parts[6]
                    func = parts[7]  
                    source_file = parts[8]
                    line_no = parts[9]
                    mem_addr_hits.append((inst_addr, mem_addr, size, exe_name, func, source_file, line_no))
                except ValueError as ve:
                    print(f"Skipped a row due to unexpected format: {line.strip()} | Error: {ve}")
                    continue

def cache_line_util(input_file, output_file):
    mem_addr_hits = []
    filter_mem_addr(input_file, mem_addr_hits)
    mem_addr_hits.sort(key=lambda x: x[1])  #Sort by memory address

    cache_line_usage = {}
    access_count = {}  #access count to each memory address
    cacheline_total_count = {}  #To track total access count per cache line
    instruction_map = {}  #Map memory addresses to corresponding instruction addresses and bytes transferred

    #Tracking which bytes in each cache line are used  
    for inst_addr, mem_addr, size, exe_name, func, source_file, line_no in mem_addr_hits:
    #for inst_addr, mem_addr, size in mem_addr_hits:
        cache_line = get_cache_line(mem_addr)
        start_offset = mem_addr % CACHE_LINE_SIZE
        end_offset = start_offset + size

        if cache_line not in cache_line_usage:
            cache_line_usage[cache_line] = [False] * CACHE_LINE_SIZE  #initialize unused bytes
            cacheline_total_count[cache_line] = 0  #initialize total access count for the cache line

        #Mark the bytes as used in the cache line, track access count
        for i in range(start_offset, min(end_offset, CACHE_LINE_SIZE)):
            if not cache_line_usage[cache_line][i]:
                cache_line_usage[cache_line][i] = True  #Mark byte as used

            #Counting and mapping memory address to instruction address and bytes transferred
            mem_address = cache_line * CACHE_LINE_SIZE + i
            if i == start_offset:
                access_count[mem_address] = access_count.get(mem_address, 0) + 1
                cacheline_total_count[cache_line] += 1
            else:
                access_count[mem_address] = access_count.get(mem_address, 0)

            #Append a tuple of (instruction_address, size) to the instruction_map
            if mem_address not in instruction_map:
                instruction_map[mem_address] = [(hex(inst_addr), size, 1, exe_name, func, source_file, line_no)]
                #instruction_map[mem_address] = [(hex(inst_addr), size, 1)]  # Store instruction, size, and count (1st occurrence)
            else:
                # Check if the instruction already exists for this memory address
                found = False
                for j in range(len(instruction_map[mem_address])):
                    if instruction_map[mem_address][j][0] == hex(inst_addr):  # Instruction address exists
                        #increment the count
                        instruction_map[mem_address][j] = (instruction_map[mem_address][j][0], instruction_map[mem_address][j][1], instruction_map[mem_address][j][2] + 1, exe_name, func, source_file, line_no)
                        found = True
                        break
                if not found:
                    #If instruction not found, add a new entry with a count of 1
                    #instruction_map[mem_address].append((hex(inst_addr), size, 1))
                    instruction_map[mem_address].append((hex(inst_addr), size, 1, exe_name, func, source_file, line_no))
    #Get the maximum number of instruction entries for any memory address
    max_instructions = max(len(instruction_map[mem_address]) for mem_address in instruction_map)

    #Prepare the header for the CSV file
    header = ['Memory Address', 'Cache Line', 'Usage', 'Used Bytes', 'Unused bytes', 'Access Count', 'Cacheline Total Count']
    for i in range(1, max_instructions + 1):
        header.append(f'Instruction Address {i}')
        header.append(f'Bytes Transferred {i}')
        header.append(f'Inst_Addr_{i}_Count')  
        header.append(f'Exe Name {i}')
        header.append(f'Func {i}')
        header.append(f'Source File {i}')
        header.append(f'Line No {i}')

    #Count used and unused bytes in each cache line
    cache_line_stats = {}
    for cache_line, usage in cache_line_usage.items():
        used_bytes = usage.count(True)  
        unused_bytes = CACHE_LINE_SIZE - used_bytes  
        cache_line_stats[cache_line] = {
            'used_bytes': used_bytes,
            'unused_bytes': unused_bytes
        }

    #Total cachelines
    total_cachelines = len(cacheline_total_count)
    output_rows = []

    for cache_line, usage in cache_line_usage.items():
        total_count_added = False
        used_bytes = cache_line_stats[cache_line]['used_bytes']  
        unused_bytes = cache_line_stats[cache_line]['unused_bytes']

        for i in range(CACHE_LINE_SIZE):
            mem_address = cache_line * CACHE_LINE_SIZE + i
            row = [hex(mem_address), hex(cache_line)]

            if usage[i]:  
                row.extend(["Used", used_bytes, unused_bytes, access_count[mem_address]])
                if not total_count_added:
                    row.append(cacheline_total_count[cache_line])
                    total_count_added = True
                else:
                    row.append('')  
                if mem_address in instruction_map:
                    instruction_entries = instruction_map[mem_address]

                    for entry in instruction_entries:
                        instr, size, count, exe_name, func, source_file, line_no = entry
                        row.extend([instr, size, count, exe_name, func, source_file, line_no])

                    remaining_slots = (max_instructions - len(instruction_entries)) * 7
                    row.extend([''] * remaining_slots)
                else:
                    row.extend([''] * (max_instructions * 7))

            else:  #unused
                row.extend(["Unused", used_bytes, unused_bytes, 0])
                if not total_count_added:
                    row.append(cacheline_total_count[cache_line])
                    total_count_added = True
                else:
                    row.append('')
                row.extend(['N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A'])

            output_rows.append(row)

    with open(output_file, 'w', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(header)
        writer.writerows(output_rows)

    print(f"Processing complete. Results written to {output_file}")

input_file = input("Name and path to the input log / txt file: ")
output_file = input("Provide a Path/name to save the first level detailed output CSV file: ")
output_csv = input("Provide a Path/name to save the unused cacheline percentage CSV file: ")

def create_dir_if_not_present(file_path):
    directory = os.path.dirname(file_path)
    if directory:  
        os.makedirs(directory, exist_ok=True)

create_dir_if_not_present(input_file)
create_dir_if_not_present(output_file)
create_dir_if_not_present(output_csv)
base_name = os.path.splitext(output_csv)[0]  
image_name = f"{base_name}_cacheline_distribution.png"
# cache line usage fn call
cache_line_util(input_file, output_file)

process_cacheline_data(output_file, output_csv, show_graph=True)

