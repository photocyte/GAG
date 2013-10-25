#!/usr/bin/env python

class Fasta:

    def __init__(self):
        self.entries = list()

    def readString(self, data):
        seq_id = ''
        seq = ''
        for line in data.split('\n'):
            if line[0] == '>':
                if len(seq_id) > 0:
                    # Save the data
                    self.entries.append([seq_id, seq])
                
                seq_id = line[1:].strip().split()[0] # Get the next seq_id
                seq = ''
            else:
                seq += line.strip()
        # Add the last sequence
        self.entries.append([seq_id, seq])

    def writeString(self):
        s = str()
        i = 0
        for entry in self.entries:
            if i != 0:
                s += '\n'
            s += '>'+entry[0]+'\n'+entry[1]
            i += 1
        return s

    def readFile(self, fileName):
        with open(fileName, 'r') as f:
            seq_id = ''
            seq = ''
            for line in f:
                if line[0] == '>':
                    if len(seq_id) > 0:
                        # Save the data
                        self.entries.append([seq_id, seq])
                
                seq_id = line[1:].strip().split()[0] # Get the next seq_id
                seq = ''
            else:
                seq += line.strip()
            # Add the last sequence
            self.entries.append([seq_id, seq])

    def trimSeq(self, seq_id, start, stop):
        for i, entry in enumerate(self.entries):
            if entry[0] == seq_id:
                if len(entry[1]) <= stop-(start-1):
                    self.entries.pop(i)
                else:
                    self.entries[i][1] = entry[1][:start-1] + entry[1][stop:]
                return
		
		

		