from Tool_Pack import tools
from dateutil.parser import parse
from operator import itemgetter
import time
import copy


class RelationCreator:
    def __init__(self):
        self.files_path = "path_to_input_files"

    def merge_months(self, year, start_month, end_month):
        year_dict = dict()
        for month in range(start_month, end_month):
            month_dict_of_tags = tools.load_pickle(self.files_path + "Scores/" + str(year) + "-" + str(month))
            for user_id, tag_list in month_dict_of_tags.items():

                if user_id in year_dict:
                    year_dict[user_id][0] += month_dict_of_tags[user_id][0]
                    for tag, tag_score in month_dict_of_tags[user_id][1].items():
                        if tag in year_dict[user_id][1]:
                            year_dict[user_id][1][tag] += tag_score
                        else:
                            year_dict[user_id][1][tag] = tag_score
                else:
                    year_dict[user_id] = tag_list
        tools.save_pickle(self.files_path + "year_scores/" + str(year), year_dict)

    def create_relations(self, year):
        start_time = time.time()
        with open(self.files_path + "Graphs/Relations/" + str(year) + "_users_relations.csv", "w") as rel_file:
            rel_file.write("Source,Target,Weight\n")
            user_tag_dict = tools.load_pickle(self.files_path + "year_scores/" + str(year))
            normalized_user_tag_dict = dict()
            for user_id, tag_list in user_tag_dict.items():
                normalized_user_tag_dict[user_id] = [tag_list[0],
                                                    self.normalize_tag_score(copy.deepcopy(tag_list[1])),
                                                    set(tag_list[1].keys())]
            all_users_ids = list(normalized_user_tag_dict.keys())
            print(len(all_users_ids))
            for idx, outer_user_id in enumerate(all_users_ids[:-1]):
                print(idx)
                for inner_user_id in all_users_ids[idx+1:]:
                    usr_distance2 = self.users_distance2(normalized_user_tag_dict[outer_user_id],
                                                         normalized_user_tag_dict[inner_user_id])

                    rel_file.write(str(outer_user_id) + ',' + str(inner_user_id) + ','
                                    + str(2 - usr_distance2) + "\n")
        tools.save_pickle(self.files_path + "year_scores/normalized_2020", normalized_user_tag_dict)
        print("execution time", time.time() - start_time)

    @staticmethod
    def normalize_tag_score(tag_dict):
        total_score = 0
        for score in tag_dict.values():
            total_score += int(score)
        for tag, score in tag_dict.items():
            tag_dict[tag] = int(score) / total_score
        return tag_dict

    @staticmethod
    def users_distance(tag_dict1, tag_dict2):
        all_tags = set()
        distance = 0.0
        for tag in tag_dict1.keys():
            all_tags.add(tag)
        for tag in tag_dict2.keys():
            all_tags.add(tag)
        for tag in all_tags:
            tag_value1 = 0.0
            tag_value2 = 0.0
            if tag in tag_dict1:
                tag_value1 = tag_dict1[tag]
            if tag in tag_dict2:
                tag_value2 = tag_dict2[tag]
            distance += abs(tag_value1 - tag_value2)
        return distance

    @staticmethod
    def users_distance2(tag_dict1, tag_dict2):
        common_tags = tag_dict1[2].intersection(tag_dict2[2])
        distance = 0.0
        sum_commons = 0.0
        for tag in common_tags:
            sum_commons += (tag_dict1[1][tag] + tag_dict2[1][tag])
            distance += abs(tag_dict1[1][tag] - tag_dict2[1][tag])

        return 2 + distance - sum_commons


if __name__ == '__main__':
    r_creator = RelationCreator()
    r_creator.merge_months(2008, 8, 13)
    for c_year in range(2009, 2021):
        r_creator.merge_months(c_year, 1, 13)
    for c_year in range(2008, 2021):
        r_creator.create_relations(c_year)
