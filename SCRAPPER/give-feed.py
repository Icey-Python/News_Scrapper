import csv 
with open('SCRAPPER/articles.csv', 'r') as file:
        # Create a CSV reader object
        reader = csv.DictReader(file)
        # Iterate over each row in the CSV file
        for row in reader:
            # Append the row (as a dictionary) to the data list
            print(row)
            
