# MIT License
# Copyright (c) 2024  GayathriNarayana19
# Permission is hereby granted to use, copy, modify, and distribute this software.

import csv

CACHE_LINE_SIZE = 64

def process_cacheline_data(input_csv, output_csv, top_n):
    cacheline_data = {}

    with open(input_csv, 'r') as infile:
        reader = csv.reader(infile)
        header = next(reader)  

        for row in reader:
            cache_line = row[1]
            usage = row[2]  
            used_bytes = int(row[3])
            unused_bytes = int(row[4])
            cacheline_total_count = row[6]

            instruction_addresses = []
            bytes_transferred = []
            inst_counts = []
            exe_names = []
            func_names = []
            source_files = []
            line_numbers = []

            for i in range(7, len(row), 7):  
                if row[i] and row[i+1].isdigit() and row[i+2].isdigit():
                    instruction_addresses.append(row[i])
                    bytes_transferred.append(int(row[i+1]))  
                    inst_counts.append(int(row[i+2]))
                    exe_names.append(row[i+3])
                    func_names.append(row[i+4])
                    source_files.append(row[i+5])
                    line_numbers.append(row[i+6])

            if cache_line not in cacheline_data:
                cacheline_data[cache_line] = {
                    'cacheline_total_count': int(cacheline_total_count) if cacheline_total_count.isdigit() else 0,
                    'used_bytes': used_bytes,
                    'unused_bytes': unused_bytes,
                    'instructions': []
                }

            for addr, size, count, exe, func, source, line in zip(instruction_addresses, bytes_transferred, inst_counts, exe_names, func_names, source_files, line_numbers):
                cacheline_data[cache_line]['instructions'].append((addr, size, count, exe, func, source, line))

    for cache_line, data in cacheline_data.items():
        data['product_unused_total_count'] = data['unused_bytes'] * data['cacheline_total_count']

    #Sort the cachelines based on the product of unused bytes and total cacheline access count
    sorted_cachelines = sorted(cacheline_data.items(), key=lambda x: x[1]['product_unused_total_count'], reverse=True)

    #Limit the output to top_n entries or all entries if the user specifies -1
    if top_n > 0:
        sorted_cachelines = sorted_cachelines[:top_n]

    #Second CSV output
    with open(output_csv, 'w', newline='') as outfile:
        writer = csv.writer(outfile)

        writer.writerow(['Cache Line', 'Used Bytes', 'Unused Bytes', 'Cacheline Total Count', 'Product (Unused Bytes * Cacheline Total Count)', 
                         'Instruction Address', 'Bytes Transferred', 'Instruction Count', 'Exe Name', 'Func', 'Source File', 'Line No'])

        for cache_line, data in sorted_cachelines:
            writer.writerow([cache_line, data['used_bytes'], data['unused_bytes'], data['cacheline_total_count'], data['product_unused_total_count'], '', '', '', '', '', '', ''])

            for instr_addr, size, count, exe, func, source, line in data['instructions']:
                writer.writerow(['', '', '', '', '', instr_addr, size, count, exe, func, source, line])

    print(f"Processing complete. Sorted cacheline data written to {output_csv}")

input_csv = input("Name and path of the first level CSV file: ")
output_csv = input("Provide a name to save the second level output CSV file : ")
top_n = int(input("Enter the number of top cachelines to process (-1 for all): "))

process_cacheline_data(input_csv, output_csv, top_n)

