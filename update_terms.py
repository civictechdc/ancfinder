import csv

history = csv.reader(open('data/historical-commissioners.csv', 'r'), delimiter=',', quoting=csv.QUOTE_MINIMAL)
contestation = csv.reader(open('data/anc-candidates-2012.csv', 'r'), delimiter=',')
h_output = csv.writer(open('data/anc-terms.csv', 'w'), delimiter=',', quotechar='/') 
c_output = csv.writer(open('data/anc-contestation.csv', 'w'), delimiter=',')

#Not sure if I used quotechar correctly, but this got the result I was trying to achieve.

terms = {}
candidates = {}

#h_output.writerow(['election_date'] + ['anc'] + ['last_name'] + ['first_name'] + ['suffix'] + ['terms'])

for row in history:
	short = str([row[3][:3] + " " + row[2][:3]])
	if row[2] == 'No candidate':
		continue
	elif short in terms:
		terms[short] += 1
		t = terms[short]
	else:
		terms[short] = 1
		t = 1
	output = [row[0]] + [row[1]] + [row[2]] + [row[3]] + [row[4]] + [t]
	if row[0][:4] == "2012":
		h_output.writerow(output)
		
for row in contestation:
	if row[1] in candidates:
		candidates[row[1]] += 1
	else:
		candidates[row[1]] = 1

for total in sorted(candidates):
	output = [total] + [candidates[total]]
	if len(total) == 4:
		c_output.writerow(output)