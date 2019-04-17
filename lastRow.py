

csvfile = '/Users/talamram/Documents/CapraHikes/hike21/meta.csv'
  with open(csvfile, 'r') as meta:
      reader = csv.reader(meta)
      lasthikephoto = 0
      lasthikedate = 0
      row_count = sum(1 for row in reader)
      print("row count:", str(row_count))
