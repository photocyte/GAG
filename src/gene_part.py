#!/usr/bin/env python

import math
import sys

def length_of_segment(index_pair):
    return math.fabs(index_pair[1] - index_pair[0]) + 1

def adjust_index_pair(index_pair, n):
    return [i + n for i in index_pair]

class GenePart:
    def __init__(self, feature_type=None, identifier=None, name=None, indices=None, score=None, parent_id=None):
        self.feature_type = feature_type
        self.identifier = []
        if identifier is not None:
            self.identifier.append(identifier)
        self.name = []
        if name is not None:
            self.name.append(name)
        self.indices = []
        if indices is not None:
            self.indices.append(indices)
        self.score = []
        if score is not None:
            self.score.append(score)
        self.parent_id = parent_id

    def __str__(self):
        result = self.feature_type + " (first ID="
        result += str(self.identifier[0]) + ", first name="
        result += str(self.name[0]) + ")"
        return result

    def add_indices(self, ind):
        if isinstance(ind, list) and len(ind) is 2:
            self.indices.append(ind)
        else:
            raise ValueError()

    def add_name(self, name):
        self.name.append(name)

    def add_identifier(self, identifier):
        self.identifier.append(identifier)

    def add_score(self, score):
        self.score.append(score)

    def length(self):
        length = 0
        for index_pair in self.indices:
            length += length_of_segment(index_pair)
        return length

    # used by .to_gff
    def get_score(self, i):
        if self.score and len(self.score) > i:
            return self.score[i]
        else:
            return "."

    # used by .to_gff
    # (CDS overrides this method)
    def get_phase(self, i):
        return "."

    def collidesRange(self, start, stop):
        for index_pair in self.indices:
            if start <= index_pair[1] and stop >= index_pair[0]:
                return True
        return False

    def remove_segment(self, segindex):
        try:
            self.identifier.pop(segindex)
            self.name.pop(segindex)
            self.indices.pop(segindex)
        except IndexError:
            sys.stderr.write("Trying to remove nonexistent segment " + str(segindex) + " from " + str(self))
        if len(self.score) > segindex:
            self.score.pop(segindex)

    def remove_trimmed_segments(self):
        segs_to_trim = []
        for i in xrange(len(self.indices)):
            if self.indices[i][0] == 0:
                segs_to_trim.append(i)
        for j in reversed(segs_to_trim):
            self.remove_segment(j)

    def adjust_indices(self, n):
        self.indices = [adjust_index_pair(pair, n) for pair in self.indices]

    def trim_end(self, endindex):
        for i, index_pair in enumerate(self.indices):
            if index_pair[0] > endindex:
                # entire segment is past cutoff;
                # mark for removal
                self.indices[i][0] = 0
                self.indices[i][1] = 0
            elif index_pair[1] > endindex:
                self.indices[i][1] = endindex

    def clean_up_indices(self):
        for i in xrange(len(self.indices)):
            if self.indices[i][1] < 1:
                self.indices[i][0] = 0
                self.indices[i][1] = 0
            elif self.indices[i][0] < 1:
                self.indices[i][0] = 1

    def valid_codon(self):  
        if length_of_segment(self.indices[0]) == 3:
            return True
        else:
            return False

    def length_of_shortest_segment(self):
        if len(self.indices) == 0:
            return None
        min_length = length_of_segment(self.indices[0])
        if len(self.indices) == 1:
            return min_length
        else:
            for index_pair in self.indices:
                if length_of_segment(index_pair) < min_length:
                    min_length = length_of_segment(index_pair)
        return min_length

    def generate_attribute_entry(self, i):
        if len(self.identifier) <= i or self.parent_id is None:
            return None
        entry = "ID=" + str(self.identifier[i]) + ";"
        if len(self.name) > i:
            entry += "Name=" + str(self.name[i]) + ";"
        entry += "Parent=" + str(self.parent_id) + "\n"
        return entry

    def to_gff(self, seq_name, source, strand):
        result = ""
        for i in range(len(self.indices)):
            result += seq_name + "\t" + source + "\t"
            result += self.feature_type + "\t" + str(self.indices[i][0])
            result += "\t" + str(self.indices[i][1]) + "\t"
            result += str(self.get_score(i)) + "\t" + strand + "\t"
            result += str(self.get_phase(i)) + "\t"
            result += self.generate_attribute_entry(i)
        return result


class CDS(GenePart):

    def __init__(self, identifier=None, name=None, indices=None, score=None, phase=None, parent_id=None):
        GenePart.__init__(self, feature_type='CDS', identifier=identifier, name=name, indices=indices, score=score, parent_id=parent_id)
        self.phase = []
        if phase is not None:
            self.phase.append(phase)
        self.annotations = []

    def get_phase(self, i):
        if self.phase and len(self.phase) > i:
            return self.phase[i]
        else:
            return "."

    def add_phase(self, ph):
        self.phase.append(ph)

    def adjust_phase(self):
        for i in range(len(self.phase)):
            if self.indices[i][0] < 1:
                self.phase[i] = (self.phase[i] + self.indices[i][0] + -1) %3


class Exon(GenePart):

    def __init__(self, **kwargs):
        kwargs['feature_type'] = 'exon'
        GenePart.__init__(self, **kwargs)
        self.annotations = []
