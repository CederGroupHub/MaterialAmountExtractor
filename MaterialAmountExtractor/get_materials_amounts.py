import os
from nltk.parse import stanford
from chemdataextractor.doc import Paragraph
from nltk.tree import ParentedTree
from operations_extractor.operations_extractor import OperationsExtractor
import copy

oe = OperationsExtractor()

os.environ["TOKENIZERS_PARALLELISM"] = "false"


class GetMaterialsAmounts:
    def __init__(self, sentence, materials_in_sentence):
        self.sentence = sentence
        self.materials_in_sentence = materials_in_sentence
        self.cut_list = ["and", "to", "presence", "into", "at the same time", ":"]
        self.sentence_cp = copy.deepcopy(self.sentence)
        self.subsentens_list = []
        self.subsentens_list_refine = []

    def get_sent_tokens(self):
        self.sent_toks = [
            tok for sent in Paragraph(self.sentence).raw_tokens for tok in sent
        ]
        return self.sent_toks

    def cut_sentence(self, cut_list, sentence):
        intersection_list = [i for i in cut_list if i in sentence]
        if len(intersection_list) >= 1:
            cut_index_start = sentence.index(intersection_list[0])
            cut_index_end = cut_index_start + 1
            subsentence1 = sentence[:cut_index_start:]
            if len(sentence) >= cut_index_start + 1:
                subsentence2 = sentence[cut_index_end::]
                self.cut_sentence(cut_list, subsentence1)
                self.cut_sentence(cut_list, subsentence2)
            else:
                self.cut_sentence(cut_list, subsentence1)

        else:
            self.subsentens_list.append(sentence)
        return self.subsentens_list

    def refine_sentence(self, subsentences_list):

        for sent_token in subsentences_list:
            cut_index_start = 0
            cut_commas_index = []
            material_indexs = []
            for i in range(len(sent_token)):
                if sent_token[i] in self.materials_indexs.keys():
                    material_indexs.append(i)
            for material_index in material_indexs:
                if material_index >= 1:
                    if sent_token[material_index - 1] == ",":
                        cut_commas_index.append(material_index - 1)
                        continue
                    if material_index >= 3:
                        if (
                                sent_token[material_index - 3] == ","
                                and sent_token[material_index - 3] != "or"
                        ):
                            cut_commas_index.append(material_index - 3)
                            continue
                        if material_index >= 4:
                            if (
                                    sent_token[material_index - 4] == ","
                                    and sent_token[material_index - 3] != "or"
                            ):
                                cut_commas_index.append(material_index - 4)
                                continue
                else:
                    continue
            if cut_commas_index:
                for comma_index in cut_commas_index:
                    cut_index_end = comma_index
                    subsentence = sent_token[cut_index_start:cut_index_end:]
                    self.subsentens_list_refine.append(" ".join(subsentence))
                    # print(self.subsentens_list_refine)
                    cut_index_start = cut_index_end + 1
                    if comma_index == cut_commas_index[-1]:
                        subsentence = sent_token[comma_index + 1::]
                        self.subsentens_list_refine.append(" ".join(subsentence))
            else:
                self.subsentens_list_refine.append(" ".join(sent_token))
        return self.subsentens_list_refine

    def delete_redundant_info(self):
        self.get_sent_tokens()
        material_indexs = []
        cut_indexs = []
        for i in range(len(self.sent_toks)):
            if self.sent_toks[i] in self.materials_indexs.keys():
                self.sent_toks[i] = self.materials_indexs[self.sent_toks[i]]
                material_indexs.append(i)

        for material_index in material_indexs:
            if material_index >= 2:
                if self.sent_toks[material_index - 1] == "(" and (
                        self.sent_toks[material_index - 2] in self.materials_in_sentence
                        or self.sent_toks[material_index - 2] == "solution"
                ):
                    cut_indexs.append(material_index)
                if self.sent_toks[material_index - 1] == "[" and (
                        self.sent_toks[material_index - 2] in self.materials_in_sentence
                        or self.sent_toks[material_index - 2] == "solution"
                ):
                    cut_indexs.append(material_index)
        if cut_indexs:
            for cut_index in cut_indexs:
                self.materials_in_sentence.remove(self.sent_toks[cut_index])
        self.sentence = " ".join(self.sent_toks)

    def MAT_replace(self):
        self.materials_indexs = {}
        i = 0
        index_end = 0
        for material in self.materials_in_sentence:
            if material in self.sentence[index_end:]:
                index_start = index_end + self.sentence[index_end:].index(material)
                index_end = index_start + len(material)
                self.sentence = (
                        self.sentence[:index_start]
                        + "MAT_NAME"
                        + str(i)
                        + self.sentence[index_end:]
                )
                self.materials_indexs["MAT_NAME" + str(i)] = material
                index_end = self.sentence.index("MAT_NAME" + str(i)) + len(
                    "MAT_NAME" + str(i)
                )
                i += 1

    def unit_replace(self):
        self.units_indexs = {}
        i = 0
        unit_list = ['mol%', 'wt.%', 'wt%', '× 10-1 mol L-1', "mol L\u22121", "mol L-1", 'm mol', "mol L−1", 'mol dm-3',
                     "g L−1", 'g L-1', 'mol/mL', 'mg mL-1', "mg mL−1", 'mmol/l', "mmol", "L-1", "μL", 'mol/l', "mol/L",
                     "mM", 'mol L- 1',
                     'mg/ml',
                     'mg/μl',
                     'mg/l',
                     'mg ml-1'
                     'mg μl-1',
                     'mg l-1',
                     'mmol/ml',
                     'mmol/μl',
                     'mmol/l',
                     'mmol ml-1'
                     'mmol μl-1',
                     'mmol l-1',
                     'μg/ml',
                     'μg/μl',
                     'μg/l',
                     'μg ml-1'
                     'μg μl-1',
                     'μg l-1',
                     'μmol/ml',
                     'μmol/μl',
                     'μmol/l',
                     'μmol ml-1'
                     'μmol μl-1',
                     'μmol l-1',
                     'g/ml',
                     'g/μl',
                     'g/l',
                     'g ml-1'
                     'g μl-1',
                     'g l-1',
                     'mol/ml',
                     'mol/μl',
                     'mol/l',
                     'mol ml-1'
                     'mol μl-1',
                     'mol l-1',
                     'mg/mL',
                     'mg/μL',
                     'mg/L',
                     'mg mL-1'
                     'mg μL-1',
                     'mg L-1',
                     'mmol/mL',
                     'mmol/μL',
                     'mmol/L',
                     'mmol mL-1'
                     'mmol μL-1',
                     'mmol L-1',
                     'μg/mL',
                     'μg/μL',
                     'μg/L',
                     'μg mL-1'
                     'μg μL-1',
                     'μg L-1',
                     'μmol/mL',
                     'μmol/μL',
                     'μmol/L',
                     'μmol mL-1'
                     'μmol μL-1',
                     'μmol L-1',
                     'g/mL',
                     'g/μL',
                     'g/L',
                     'g mL-1'
                     'g μL-1',
                     'g L-1',
                     'mol/mL',
                     'mol/μL',
                     'mol/L',
                     'mol mL-1'
                     'mol μL-1',
                     'mol L-1',
                     'μM',
                     'nM'
                     ]
        unit_list.sort(key=len, reverse=True)
        for unit in unit_list:
            while unit in self.sentence:
                index_start = self.sentence.index(unit)
                index_end = index_start + len(unit)
                self.sentence = (
                        self.sentence[:index_start]
                        + "UNIT"
                        + str(i)
                        + self.sentence[index_end:]
                )
                self.units_indexs["UNIT" + str(i)] = unit
                i += 1

    def clean_MAT_for_Tree(self, tree_with_MAT):
        ptree = ParentedTree.fromstring(str(tree_with_MAT))
        leaf_values = ptree.leaves()
        for value in leaf_values:
            if value in self.materials_indexs.keys():
                leaf_index = leaf_values.index(value)
                tree_location = ptree.leaf_treeposition(leaf_index)  # get a tuple
                tree_location = list(tree_location)  # tuple to list
                ptree[tree_location] = self.materials_indexs[value]
                leaf_values = ptree.leaves()
            if value in self.units_indexs.keys():
                leaf_index = leaf_values.index(value)
                tree_location = ptree.leaf_treeposition(leaf_index)
                tree_location = list(tree_location)
                ptree[tree_location] = self.units_indexs[value]
                leaf_values = ptree.leaves()
        return ptree

    def get_materials_copy(self):
        self.materials_copy = copy.deepcopy(self.materials_in_sentence)
        return self.materials_copy

    def find_larges_tree_for_materials(self, Tree, materials_in_subsentence):
        subtree_list = []

        def findTheTree(subtree):
            parent = subtree.parent()
            if parent:
                leave_values = parent.leaves()
                intersection_list = [
                    i for i in leave_values if i in materials_in_subsentence
                ]
                if len(intersection_list) == 1:
                    findTheTree(parent)
                else:
                    if subtree.leaves() not in subtree_list:
                        subtree_list.append(subtree.leaves())
            else:
                if subtree.leaves() not in subtree_list:
                    subtree_list.append(subtree.leaves())

        for subtree in Tree.subtrees(lambda t: t.height() == 2):  # 找tag-word对
            leave_values = subtree.leaves()

            for material in materials_in_subsentence:
                if material in leave_values:
                    parent = subtree.parent()
                    if parent:
                        leave_values = parent.leaves()
                        intersection_list = [
                            i for i in leave_values if i in materials_in_subsentence
                        ]
                        if len(intersection_list) == 1:
                            findTheTree(parent)
                        elif "and" in leave_values:
                            and_index = leave_values.index("and")
                            list1 = leave_values[:and_index:]
                            list2 = leave_values[and_index::]
                            if list1 not in subtree_list:
                                subtree_list.append(list1)
                            if list2 not in subtree_list:
                                subtree_list.append(list2)
                        elif "to" in leave_values:
                            and_index = leave_values.index("to")
                            list1 = leave_values[:and_index:]
                            list2 = leave_values[and_index::]
                            if list1 not in subtree_list:
                                subtree_list.append(list1)
                            if list2 not in subtree_list:
                                subtree_list.append(list2)
                        elif "with" in leave_values:
                            and_index = leave_values.index("with")
                            list1 = leave_values[:and_index:]
                            list2 = leave_values[and_index::]
                            if list1 not in subtree_list:
                                subtree_list.append(list1)
                            if list2 not in subtree_list:
                                subtree_list.append(list2)

                        else:
                            if subtree.leaves() not in subtree_list:
                                subtree_list.append(subtree.leaves())

        return subtree_list

    def find_amounts_for_materials_tree(self, tree_list, materials_in_subsentence):
        Material_and_amounts = {}
        unit_list = ['g', 'mg', 'mmol', 'l', 'ml', 'mL', '%', 'M', 'mM', 'cm3', 'mol%', 'wt.%', 'wt', 'mol L-1', 'mol L−1',
                     'mol L−1', 'mg mL−1', 'L', '-', '−', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'mol',
                     'L-1', 'μL', 'μl', 'mol/L', 'cc', 'mol L-1', 'mol L- 1', '× 10-1 mol L-1', 'mol/mL', 'mol dm-3',
                     'mmol/l', 'mol/l', 'm mol', 'mg mL-1', 'wt%', 'g L-1',
                     'mg/ml',
                     'mg/μl',
                     'mg/l',
                     'mg ml-1'
                     'mg μl-1',
                     'mg l-1',
                     'mmol/ml',
                     'mmol/μl',
                     'mmol/l',
                     'mmol ml-1'
                     'mmol μl-1',
                     'mmol l-1',
                     'μg/ml',
                     'μg/μl',
                     'μg/l',
                     'μg ml-1'
                     'μg μl-1',
                     'μg l-1',
                     'μmol/ml',
                     'μmol/μl',
                     'μmol/l',
                     'μmol ml-1'
                     'μmol μl-1',
                     'μmol l-1',
                     'g/ml',
                     'g/μl',
                     'g/l',
                     'g ml-1'
                     'g μl-1',
                     'g l-1',
                     'mol/ml',
                     'mol/μl',
                     'mol/l',
                     'mol ml-1'
                     'mol μl-1',
                     'mol l-1',
                     'mg/mL',
                     'mg/μL',
                     'mg/L',
                     'mg mL-1'
                     'mg μL-1',
                     'mg L-1',
                     'mmol/mL',
                     'mmol/μL',
                     'mmol/L',
                     'mmol mL-1'
                     'mmol μL-1',
                     'mmol L-1',
                     'μg/mL',
                     'μg/μL',
                     'μg/L',
                     'μg mL-1'
                     'μg μL-1',
                     'μg L-1',
                     'μmol/mL',
                     'μmol/μL',
                     'μmol/L',
                     'μmol mL-1'
                     'μmol μL-1',
                     'μmol L-1',
                     'g/mL',
                     'g/μL',
                     'g/L',
                     'g mL-1'
                     'g μL-1',
                     'g L-1',
                     'mol/mL',
                     'mol/μL',
                     'mol/L',
                     'mol mL-1'
                     'mol μL-1',
                     'mol L-1',
                     'μM',
                     'nM',
                     'm']

        unit_list.sort(key=len, reverse=True)
        print(unit_list[0])

        def isnumber(string):
            try:
                float(string)
                return True
            except:
                return False

        for material in materials_in_subsentence:
            if material in tree_list:
                amounts = []
                for i, element in enumerate(tree_list):
                    print(element)
                    if isnumber(element):
                        unit_index = i + 1
                        if unit_index < len(tree_list):
                            # Account for scientific notation
                            if tree_list[unit_index] == '×':
                                if i+5 < len(tree_list) and tree_list[i+3] == '^':
                                    # Account for 10^<digit> case
                                    element = element + tree_list[i+1] + tree_list[i+2] + tree_list[i+3] + tree_list[i+4]
                                    tree_list[i+1] == 'SCINO' + tree_list[i+1] # mask 10 base
                                    tree_list[i+4] == 'SCINO' + tree_list[i+4] # mask exponent
                                    unit_index = i + 5
                                elif i+3 < len(tree_list):
                                    element = element + tree_list[i+1] + tree_list[i+2]
                                    tree_list[i+2] == 'SCINO' + tree_list[i+2] # mask 10 base and exponent
                                    unit_index = i + 3

                            if tree_list[unit_index] in unit_list or tree_list[unit_index].lower() in unit_list:
                                amounts.append(element)
                                amounts.append(tree_list[unit_index])
                                Material_and_amounts[material] = amounts
                                continue
        return Material_and_amounts

    def get_new_cut_list(self):
        operation_in_sent = oe.get_operations_labels(self.sent_toks)
        self.cut_list += operation_in_sent

    def clean_brackets(self):
        while "(" in self.sent_toks:
            self.sent_toks.remove("(")
        while ")" in self.sent_toks:
            self.sent_toks.remove(")")
        while "respectively" in self.sent_toks:
            self.sent_toks.remove("respectively")
        while "of" in self.sent_toks:
            self.sent_toks.remove("of")
        return self.sent_toks

    def clean_sentence(self):
        self.sentence = self.sentence.replace('\u2212', '-')
        while "at the same time" in self.sentence:
            self.sentence = self.sentence.replace("at the same time", "and")
        while "with the addition" in self.sentence:
            self.sentence = self.sentence.replace("with the addition", "and")
        while "by the addition" in self.sentence:
            self.sentence = self.sentence.replace("by the addition", "and")
        if (
                "stainless-steel" in self.materials_in_sentence
                and "Teflon" in materials_in_sentence
        ):
            self.materials_in_sentence.remove("stainless-steel")
        if (
                "stainless steel" in self.materials_in_sentence
                and "Teflon" in materials_in_sentence
        ):
            self.materials_in_sentence.remove("stainless steel")
        return self.sentence

    def find_materials_in_subsentence(self, sent):
        materials_in_subsentence = []
        for material_index in self.materials_indexs:
            if material_index in sent:
                materials_in_subsentence.append(self.materials_indexs[material_index])
        return materials_in_subsentence

    def final_result(self):
        self.clean_sentence()
        self.MAT_replace()
        self.unit_replace()
        self.delete_redundant_info()
        self.MAT_replace()
        self.get_sent_tokens()
        self.get_new_cut_list()
        materials_and_amounts = {}
        self.clean_brackets()
        subsentences = self.cut_sentence(self.cut_list, self.sent_toks)
        new_subsentences = self.refine_sentence(subsentences)
        for sent in new_subsentences:
            if sent:
                materials_in_subsentence = self.find_materials_in_subsentence(sent)
                result = tree_parser.raw_parse(sent)
                result = next(result)

                final_tree = self.clean_MAT_for_Tree(result)
                LargestTree_list = self.find_larges_tree_for_materials(
                    final_tree, materials_in_subsentence
                )
                for tree in LargestTree_list:
                    material_and_amount = self.find_amounts_for_materials_tree(
                        tree, materials_in_subsentence
                    )
                    # print(material_and_amount)
                    if material_and_amount:
                        for material in material_and_amount:
                            if material in materials_and_amounts.keys():
                                materials_and_amounts[material] += material_and_amount[
                                    material
                                ]
                            else:
                                materials_and_amounts[material] = material_and_amount[
                                    material
                                ]
        if materials_and_amounts:
            self.materials_and_amounts = materials_and_amounts
            return self.materials_and_amounts

file_path = os.path.dirname(__file__)
stanford_parser_folder = os.path.join(file_path, 'rsc/stanfordParser')
stanford_model_path = os.path.join(file_path, 'rsc/stanfordParser/englishPCFG.ser.gz')
# stanford_parser_folder = "rsc/stanfordParser"
# stanford_model_path = "rsc/stanfordParser/englishPCFG.ser.gz"
os.environ["STANFORD_PARSER"] = stanford_parser_folder
os.environ["CLASSPATH"] = stanford_parser_folder
os.environ["STANFORD_MODELS"] = stanford_parser_folder

# print(os.environ)

tree_parser = stanford.StanfordParser(model_path=stanford_model_path)

if __name__ == "__main__":
    materials_in_sentence = ["NaOH", "ZnCl2", "SnCl4"]
    gold_mats = [
        'citrate',
        'HAuCl4',
    ]
    sentence = "In a common preparation, equal volume of 0.6×10-4 mmol NaOH and 0.1 mol L−1 ZnCl2 aqueous solution " \
               "was added into subsequently 0.1 mol L−1 SnCl4 solution with magnetic stirring at room temperature."
    gold_sent = "AuNSs were prepared following a seed mediated growth method already reported.The seed solution was prepared by adding 5 mL of 34 × 10−3 m citrate solution to 95 mL of boiling 0.5 × 10−3 m HAuCl4 solution under vigorous stirring."
    m_m = GetMaterialsAmounts(gold_sent, gold_mats)
    print(m_m.final_result())
    print("down!")
