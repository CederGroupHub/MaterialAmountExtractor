import os
import json
from bson import json_util
from nltk.parse import stanford
import chemdataextractor as CDE
from chemdataextractor.doc import Paragraph
from nltk.tree import ParentedTree
from operations_extractor.operations_extractor import OperationsExtractor
import copy

oe = OperationsExtractor()


class get_materials_amounts:
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

    def CutSentence(self, cut_list, sent_toks):
        intersection_list = [i for i in cut_list if i in sent_toks]
        #         print(intersection_list)
        if len(intersection_list) >= 1:
            cut_index = sent_toks.index(intersection_list[0])
            subsentens1 = sent_toks[:cut_index:]
            if len(sent_toks) >= cut_index + 1:
                subsentens2 = sent_toks[cut_index + 1 : :]
                self.CutSentence(cut_list, subsentens1)
                self.CutSentence(cut_list, subsentens2)
            else:
                self.CutSentence(cut_list, subsentens1)

        else:
            self.subsentens_list.append(sent_toks)
        return self.subsentens_list

    def RefineSentence(self, subsentens_list):
        cut_index_start = 0
        cut_commas_index = []
        for sentence in subsentens_list:

            commas_index = [i for i in range(len(sentence)) if sentence[i] == ","]
            # print(commas_index)
            for comma_index in commas_index:
                if len(sentence) >= comma_index + 2:
                    if sentence[comma_index + 1] in materials_in_sentence:
                        cut_commas_index.append(comma_index)
            # print(cut_commas_index)
            if cut_commas_index:
                for comma_index in cut_commas_index:
                    cut_index_end = comma_index
                    subsentence = sentence[cut_index_start:cut_index_end:]
                    self.subsentens_list_refine.append(subsentence)
                    cut_index_start = cut_index_end + 1
                    if comma_index == cut_commas_index[-1]:
                        subsentence = sentence[comma_index + 1 : :]
                        self.subsentens_list_refine.append(subsentence)
                cut_index_start = 0
            else:
                self.subsentens_list_refine.append(sentence)
        # print(subsentens_list_refine)
        return self.subsentens_list_refine

    def NewCutSentence(self, cut_list, sentence):
        intersection_list = [i for i in cut_list if i in sentence]
        #         print(intersection_list)
        if len(intersection_list) >= 1:
            cut_index_start = sentence.index(intersection_list[0])
            cut_index_end = cut_index_start + len(intersection_list[0])
            subsentens1 = sentence[:cut_index_start]
            if len(sentence) >= cut_index_start + 1:
                subsentens2 = sentence[cut_index_end + 1 :]
                self.NewCutSentence(cut_list, subsentens1)
                self.NewCutSentence(cut_list, subsentens2)
            else:
                self.NewCutSentence(cut_list, subsentens1)

        else:
            self.subsentens_list.append(sentence)
        return self.subsentens_list

    def better_cut_sentence(self, cut_list, sentence):
        intersection_list = [i for i in cut_list if i in sentence]
        #         print(intersection_list)
        if len(intersection_list) >= 1:
            cut_index_start = sentence.index(intersection_list[0])
            cut_index_end = cut_index_start + 1
            subsentence1 = sentence[:cut_index_start:]
            if len(sentence) >= cut_index_start + 1:
                subsentence2 = sentence[cut_index_end::]
                self.better_cut_sentence(cut_list, subsentence1)
                self.better_cut_sentence(cut_list, subsentence2)
            else:
                self.better_cut_sentence(cut_list, subsentence1)

        else:
            self.subsentens_list.append(sentence)
        # print(self.subsentens_list)
        return self.subsentens_list

    # def first_cut(self):
    #     cut_index_start = 0
    #     cut_commas_index = []
    #     for material_index in self.mat_index:
    #         if material_index <= 2:
    #             continue
    #         elif self.sentence[material_index - 2] == ",":
    #             cut_commas_index.append(material_index - 2)
    #         elif material_index >= 9:
    #             if sentence[material_index - 2] == ",":
    #                 # print(material_index)
    #                 cut_commas_index.append(material_index - 2)
    #             elif sentence[material_index - 9] == ",":
    #                 cut_commas_index.append(material_index - 9)

    def better_refine_sentence(self, subsentences_list):

        for sent_token in subsentences_list:
            # print(sent_token)
            cut_index_start = 0
            cut_commas_index = []
            material_indexs = []
            # print(sent_token)
            for i in range(len(sent_token)):
                if sent_token[i] in self.materials_indexs.keys():
                    material_indexs.append(i)
            # print(material_indexs)
            for material_index in material_indexs:
                if material_index >= 1:
                    # print(material_index)
                    # print(sent_token)
                    # print(sent_token[material_index - 1])
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
                # print(cut_commas_index)
                for comma_index in cut_commas_index:
                    cut_index_end = comma_index
                    subsentence = sent_token[cut_index_start:cut_index_end:]
                    self.subsentens_list_refine.append(" ".join(subsentence))
                    # print(self.subsentens_list_refine)
                    cut_index_start = cut_index_end + 1
                    if comma_index == cut_commas_index[-1]:
                        subsentence = sent_token[comma_index + 1 : :]
                        self.subsentens_list_refine.append(" ".join(subsentence))
            else:
                self.subsentens_list_refine.append(" ".join(sent_token))
        return self.subsentens_list_refine

    def new_delete_redundant_info(self):
        self.get_sent_tokens()
        material_indexs = []
        cut_indexs = []
        for i in range(len(self.sent_toks)):
            if self.sent_toks[i] in self.materials_indexs.keys():
                self.sent_toks[i] = self.materials_indexs[self.sent_toks[i]]
                material_indexs.append(i)
        # print(self.sent_toks)

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
                # print(cut_index)
                self.materials_in_sentence.remove(self.sent_toks[cut_index])
        self.sentence = " ".join(self.sent_toks)
        # print(self.materials_in_sentence)

    def better_MAT_replace(self):
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
        # print(self.materials_indexs)
        # print(self.sentence)

    def better_unit_replace(self):
        self.units_indexs = {}
        i = 0
        unit_list = ["mol L−1", "g L−1", "mg mL−1", "mmol", "L-1", "μL", "mol/L", "mM"]
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

    def newMATreplace(self):
        for material in self.materials_in_sentence:
            if material in self.sentence:
                index_start = self.sentence.index(material)
                index_end = index_start + len(material)
                self.sentence = (
                    self.sentence[:index_start] + "MAT_NAME" + self.sentence[index_end:]
                )
        return self.sentence

    def betterUNITReplace(self):
        unit_list = ["mol L−1", "g L−1", "mg mL−1", "mmol", "L-1", "μL", "mol/L", "mM"]
        self.units_in_sentence = []

        def replaceUnit(sentence, unit_list, unitinsentence):
            for unit in unit_list:
                if unit in sentence:
                    # print(unit)
                    index_start = sentence.index(unit)
                    # print(index_start)
                    index_end = index_start + len(unit)
                    sentence = sentence[:index_start] + "UNIT" + sentence[index_end:]
                    # print(sentence)
                    unitinsentence.append(unit)
                    break
            for unit in unit_list:
                if unit in sentence:
                    sentence, unitinsentence = replaceUnit(
                        sentence, unit_list, unitinsentence
                    )
            # print(sentence, unitinsentence)
            return sentence, unitinsentence

        self.sentence, self.units_in_sentence = replaceUnit(
            self.sentence, unit_list, self.units_in_sentence
        )
        # print(self.sentence)
        return self.sentence, self.units_in_sentence

    def cleanMATforTree(self, tree_with_MAT):
        ptree = ParentedTree.fromstring(str(tree_with_MAT))
        leaf_values = ptree.leaves()
        # print(leaf_values)
        for value in leaf_values:
            if value in self.materials_indexs.keys():
                leaf_index = leaf_values.index(value)
                tree_location = ptree.leaf_treeposition(leaf_index)  # get a tuple
                tree_location = list(tree_location)  # tuple to list
                # print(ptree[tree_location])
                # print(materials_in_sentence)
                # ptree[tree_location] = self.materials_in_sentence.pop(0)
                ptree[tree_location] = self.materials_indexs[value]
                # print(ptree[tree_location])
                leaf_values = ptree.leaves()
            if value in self.units_indexs.keys():
                leaf_index = leaf_values.index(value)
                tree_location = ptree.leaf_treeposition(leaf_index)
                tree_location = list(tree_location)
                # print(ptree[tree_location])
                # print(materials_in_sentence)
                # ptree[tree_location] = self.units_in_sentence.pop(0)
                ptree[tree_location] = self.units_indexs[value]
                # print(ptree[tree_location])
                leaf_values = ptree.leaves()
        return ptree

    def get_materials_copy(self):
        self.materials_copy = copy.deepcopy(self.materials_in_sentence)
        return self.materials_copy

    def newfindLargestTreeForMaterials(self, Tree, materials_in_subsentence):
        intersection_list = []
        subtree_list = []
        a = Tree.height()

        def findTheTree(subtree):
            parent = subtree.parent()
            if parent:
                # print(parent)
                leave_values = parent.leaves()
                # print(leave_values)
                intersection_list = [
                    i for i in leave_values if i in materials_in_subsentence
                ]
                if len(intersection_list) == 1:
                    findTheTree(parent)
                else:
                    subtree_list.append(subtree.leaves())
            else:
                subtree_list.append(subtree.leaves())

        for subtree in Tree.subtrees(lambda t: t.height() == 2):  # 找tag-word对
            leave_values = subtree.leaves()
            # print(leave_values)

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
                            subtree_list.append(list1)
                            subtree_list.append(list2)
                        elif "to" in leave_values:
                            and_index = leave_values.index("to")
                            list1 = leave_values[:and_index:]
                            list2 = leave_values[and_index::]
                            subtree_list.append(list1)
                            subtree_list.append(list2)
                        elif "with" in leave_values:
                            and_index = leave_values.index("with")
                            list1 = leave_values[:and_index:]
                            list2 = leave_values[and_index::]
                            subtree_list.append(list1)
                            subtree_list.append(list2)

                        else:
                            subtree_list.append(subtree.leaves())

        return subtree_list

    def newfindAmountsforMaterialsinTree(self, tree_list, materials_in_subsentence):
        Material_and_amounts = {}
        unit_list = [
            "g",
            "mg",
            "mmol",
            "ml",
            "mL",
            "%",
            "M",
            "mM",
            "cm3",
            "wt",
            "mol L−1",
            "mg mL−1",
            "L",
            "−",
            "1",
            "×",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "0",
            "mol",
            "L-1",
            "μL",
            "mol/L",
            "cc",
        ]

        def isnumber(string):
            try:
                float(string)
                return True
            except:
                return False

        #    leave_values=tree.leaves()
        for material in materials_in_subsentence:
            if material in tree_list:
                # print(material)
                amounts = []
                for element in tree_list:
                    if isnumber(element):
                        unit_index = tree_list.index(element) + 1
                        if unit_index < len(tree_list):
                            # print('ok')
                            if tree_list[unit_index] in unit_list:
                                amounts.append(element)
                                amounts.append(tree_list[unit_index])
                                Material_and_amounts[material] = amounts
                                # if material in Material_and_amounts.keys():
                                # aterial_and_amounts[material].append(amounts)

                                # else:
                                # Material_and_amounts[material]=amounts
                                # print(Material_and_amounts)
        return Material_and_amounts

    def get_new_cut_list(self):
        operations, spacy_tokens = oe.get_operations(self.sent_toks)
        updated_operations = oe.operations_correction(
            spacy_tokens, operations, parsed_tokens=True
        )

        updated_operations = oe.find_aqueous_mixing(
            spacy_tokens, updated_operations, parsed_tokens=True
        )
        for operation in updated_operations:
            op = self.sent_toks[operation[0]]
            # print(op)
            self.cut_list.append(op)

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
        # print(self.sentence)
        self.clean_sentence()
        self.better_MAT_replace()
        self.better_unit_replace()
        self.new_delete_redundant_info()
        # self.newMATreplace()
        self.better_MAT_replace()
        # print(self.materials_indexs)

        # self.betterUNITReplace()
        self.get_sent_tokens()
        self.get_new_cut_list()
        materials_and_amounts = {}
        self.clean_brackets()
        subsentences = self.better_cut_sentence(self.cut_list, self.sent_toks)
        # print(subsentences)
        new_subsentences = self.better_refine_sentence(subsentences)
        for sent in new_subsentences:
            if sent:
                # print(sent)
                materials_in_subsentence = self.find_materials_in_subsentence(sent)
                # materials_in_sentence_cp = self.get_materials_copy()
                result = tree_parser.raw_parse(sent)
                result = next(result)

                final_tree = self.cleanMATforTree(result)
                # final_tree.draw()
                LargestTree_list = self.newfindLargestTreeForMaterials(
                    final_tree, materials_in_subsentence
                )
                for tree in LargestTree_list:
                    material_and_amount = {}
                    # print(tree)
                    material_and_amount = self.newfindAmountsforMaterialsinTree(
                        tree, materials_in_subsentence
                    )
                    # print(material_and_amount, materials_and_amounts)
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
                    # materials_and_amounts = dict(
                    #     materials_and_amounts, **material_and_amount
                    # )
        #                 print(material_and_amount)
        if materials_and_amounts:
            #             print(m_m.sentence_cp,materials_in_sentence_cp)
            self.materials_and_amounts = materials_and_amounts
            return self.materials_and_amounts


def CDEcutsentences(text):
    sentences = []
    para = CDE.doc.Paragraph(text)
    for i in para.sentences:
        sentences.append(str(i))
    return sentences


def materialsinsentence(sentence, materials_in_paragraph):
    materials_in_sentence = []
    for material in materials_in_paragraph:
        if material["sentence"] == sentence:
            materials_in_sentence.append(material["text"])
    return materials_in_sentence


stanford_parser_folder = "rsc/stanfordParser"
stanford_model_path = "rsc/stanfordParser/englishPCFG.ser.gz"
os.environ["STANFORD_PARSER"] = stanford_parser_folder
os.environ["STANFORD_MODELS"] = stanford_parser_folder

tree_parser = stanford.StanfordParser(model_path=stanford_model_path)

if __name__ == "__main__":

    materials_in_sentence = ["NH4F", "NH4F"]
    targets = ["LaCoO3"]

    sentence = "Then, a suitable volume of NH4F solution (1.0 mol L−1) was added to the above solution to let the concentration of NH4F in the solution be at 0.25 mol L−1."
    # cut_list = ["and", "to", "presence", "into", "at the same time", ":"]  # with?
    m_m = get_materials_amounts(sentence, materials_in_sentence)
    # sent_toks = m_m.get_sent_tokens()
    # m_m.get_new_cut_list()
    print(m_m.final_result())
    print("down!")

    # with open("filtered_small_data.json", encoding="utf-8") as f:
    #     test = json.load(f)
    #     paragraph_number = 0
    #     all_paragraphs_info = []
    #     print(len(test))
    #     for element in test:
    #         try:
    #             paragraph_info = {}
    #             paragraph_number += 1
    #             materials_and_amounts_in_paragraph = {}
    #             print(paragraph_number)
    #             paragraph = element["text"]
    #             materials_list = element["materials"]
    #             # print(materials_list)
    #             paragraph_info["DOI"] = element["DOI"]
    #             paragraph_info["paragraph"] = paragraph
    #             paragraph_info["materials"] = [p["text"] for p in materials_list]
    #             targets_list = element["targets"]
    #             paragraph_info["targets"] = [p["text"] for p in targets_list]
    #             sentences = CDEcutsentences(paragraph)
    #             for sentence in sentences:
    #                 materials_and_amounts = {}
    #                 cut_list = [
    #                     "and",
    #                     "to",
    #                     "presence",
    #                     "into",
    #                     "at the same time",
    #                     "in",
    #                     ":",
    #                 ]
    #                 materials_in_sentence = materialsinsentence(
    #                     sentence, materials_list
    #                 )
    #                 # print(materials_in_sentence)
    #                 m_m = get_materials_amounts(
    #                     sentence, materials_in_sentence, cut_list
    #                 )
    #                 # print(sentence)
    #                 materials_and_amounts = m_m.final_result()
    #                 if materials_and_amounts:
    #                     for material in materials_and_amounts:
    #                         if material in materials_and_amounts_in_paragraph.keys():
    #                             materials_and_amounts_in_paragraph[
    #                                 material
    #                             ] += materials_and_amounts[material]
    #                         else:
    #                             materials_and_amounts_in_paragraph[
    #                                 material
    #                             ] = materials_and_amounts[material]
    #             print(paragraph)
    #             print(paragraph_info["materials"])
    #             print(materials_and_amounts_in_paragraph)
    #             paragraph_info["amounts"] = materials_and_amounts_in_paragraph
    #             all_paragraphs_info.append(paragraph_info)
    #             # if paragraph_number == 10:
    #             #     break
    #
    #         except Exception as e:
    #             print("bug", paragraph)
    #             print(e)
    #             continue
    # with open("m_m_small_data3.json", "w") as fw:
    #     json.dump(all_paragraphs_info, fw, indent=2, default=json_util.default)
    # print(len(all_paragraphs_info))

    with open("filtered_large_data2.json", encoding="utf-8") as f:
        test = json.load(f)
        paragraph_number = 0
        all_paragraphs_info = []
        print(len(test))
        for element in test:
            try:
                paragraph_info = {}
                paragraph_number += 1
                materials_and_amounts_in_paragraph = {}
                print(paragraph_number)
                paragraph = element["paragraph_text"]
                materials_list = element["materials"]["all_materials"]
                # print(materials_list)
                paragraph_info["DOI"] = element["doi"]
                paragraph_info["paragraph"] = paragraph
                paragraph_info["materials"] = [p["text"] for p in materials_list]
                targets_list1 = element["materials"]["target"]
                targets_list2 = element["abstract_materials"]["target"]
                if targets_list1:
                    targets_list = targets_list1
                else:
                    targets_list = targets_list2
                paragraph_info["targets"] = [p["text"] for p in targets_list]
                print(paragraph_info["targets"])
                sentences = CDEcutsentences(paragraph)
                for sentence in sentences:
                    materials_and_amounts = {}
                    materials_in_sentence = materialsinsentence(
                        sentence, materials_list
                    )
                    # print(materials_in_sentence)
                    m_m = get_materials_amounts(sentence, materials_in_sentence)
                    # print(sentence)
                    materials_and_amounts = m_m.final_result()
                    if materials_and_amounts:
                        for material in materials_and_amounts:
                            if material in materials_and_amounts_in_paragraph.keys():
                                materials_and_amounts_in_paragraph[
                                    material
                                ] += materials_and_amounts[material]
                            else:
                                materials_and_amounts_in_paragraph[
                                    material
                                ] = materials_and_amounts[material]
                print(paragraph)
                print(paragraph_info["materials"])
                print(materials_and_amounts_in_paragraph)
                paragraph_info["amounts"] = materials_and_amounts_in_paragraph
                all_paragraphs_info.append(paragraph_info)
                # if paragraph_number == 10:
                #     break

            except Exception as e:
                print("bug", paragraph)
                print(e)
                continue
    with open("m_m_large_data2.json", "w") as fw:
        json.dump(all_paragraphs_info, fw, indent=2, default=json_util.default)
    print(len(all_paragraphs_info))

    # with open("filtered_small_data.json", encoding="utf-8") as f:
    #     test = json.load(f)
    #     paragraph_number = 0
    #     all_paragraphs_info = []
    #     print(len(test))
    #     for element in test:
    #         paragraph_info = {}
    #         materials_and_amounts_in_paragraph = {}
    #         paragraph = element["text"]
    #         materials_list = element["materials"]
    #         # print(materials_list)
    #         paragraph_info["DOI"] = element["DOI"]
    #         if element["DOI"] == "10.1149/2.046404jes":
    #             paragraph_info["paragraph"] = paragraph
    #             paragraph_info["materials"] = [p["text"] for p in materials_list]
    #             targets_list = element["targets"]
    #             paragraph_info["targets"] = [p["text"] for p in targets_list]
    #             sentences = CDEcutsentences(paragraph)
    #             for sentence in sentences:
    #                 print(sentence)
    #                 materials_and_amounts = {}
    #                 materials_in_sentence = materialsinsentence(
    #                     sentence, materials_list
    #                 )
    #                 # print(materials_in_sentence)
    #                 print(materials_in_sentence)
    #                 m_m = get_materials_amounts(
    #                     sentence, materials_in_sentence
    #                 )
    #                 # print(sentence)
    #                 materials_and_amounts = m_m.final_result()
    #                 print(materials_and_amounts)
    #                 if materials_and_amounts:
    #                     for material in materials_and_amounts:
    #                         if material in materials_and_amounts_in_paragraph.keys():
    #                             materials_and_amounts_in_paragraph[
    #                                 material
    #                             ] += materials_and_amounts[material]
    #                         else:
    #                             materials_and_amounts_in_paragraph[
    #                                 material
    #                             ] = materials_and_amounts[material]
    #             print(paragraph)
    #             print(paragraph_info["materials"])
    #             print(materials_and_amounts_in_paragraph)
    #             paragraph_info["amounts"] = materials_and_amounts_in_paragraph
    #             all_paragraphs_info.append(paragraph_info)
    #             print("Done!")

    #
