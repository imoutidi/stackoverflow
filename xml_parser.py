import xml.etree.ElementTree as eTree
from xml.etree.ElementTree import ParseError
from Tool_Pack import tools
# library = python-dateutil
from dateutil.parser import parse
from collections import defaultdict


class StackParser:
    def __init__(self):
        self.folder_path = "path_to_folder"
        self.users_dict = dict()

    def parse_users(self):
        with open(self.folder_path + "Users.xml") as xml_file:
            next(xml_file)
            next(xml_file)
            for line in xml_file:
                # print(line)
                try:
                    user_info = eTree.fromstring(line)
                    self.users_dict[user_info.attrib["Id"]] = (user_info.attrib["Reputation"],
                                                               user_info.attrib["DisplayName"])
                except UnicodeDecodeError as ue:
                    encoded_line = line.encode("latin-1", "ignore")
                    user_info = eTree.fromstring(encoded_line)
                    self.users_dict[user_info.attrib["Id"]] = (user_info.attrib["Reputation"],
                                                               user_info.attrib["DisplayName"])
                except ParseError as pe:
                    print("Parse error occurred " + line)
        tools.save_pickle(self.folder_path + "/Users.pickle", self.users_dict)

    def parse_votes(self, year):
        # I will parse votes for each month
        date_list_dict = defaultdict(list)
        with open(self.folder_path + "Votes/Votes.xml") as xml_file:
            # ignoring meta info and the first six votes because they are on the
            # last day of July and we want one month windows.
            for i in range(8):
                next(xml_file)
            post_count = 0
            false_date = 0
            for line in xml_file:
                if post_count % 1000000 == 0:
                    print(post_count)
                    print(false_date)
                post_count += 1
                try:
                    vote_info = eTree.fromstring(line)
                    cur_date_obj = parse(vote_info.attrib["CreationDate"])
                    year_month = str(cur_date_obj.year) + "-" + str(cur_date_obj.month)
                    false_date = year_month
                    # messy way to deal with but the dataset has unordered dates
                    if cur_date_obj.year != year:
                        continue
                    date_list_dict[year_month].append((vote_info.attrib["Id"],
                                                       vote_info.attrib["PostId"],
                                                       vote_info.attrib["VoteTypeId"],
                                                       vote_info.attrib["CreationDate"]))

                except UnicodeDecodeError as ue:
                    encoded_line = line.encode("latin-1", "ignore")
                    vote_info = eTree.fromstring(encoded_line)
                    cur_date_obj = parse(vote_info.attrib["CreationDate"])
                    year_month = str(cur_date_obj.year) + "-" + str(cur_date_obj.month)
                    if cur_date_obj.year != year:
                        continue
                    date_list_dict[year_month].append((vote_info.attrib["Id"],
                                                       vote_info.attrib["PostId"],
                                                       vote_info.attrib["VoteTypeId"],
                                                       vote_info.attrib["CreationDate"]))

                except ParseError as pe:
                    print("Parse error occurred " + line)

            for date, vote_list in date_list_dict.items():
                tools.save_pickle(self.folder_path + "Votes/votes_per_month/" + date, vote_list)
            print("Total Number of votes: ", post_count)


    def parse_posts(self):
        with open(self.folder_path + "Posts/Posts.xml") as xml_file:
            # ignoring meta info and the first six votes because they are on the
            # last day of July and we want one month windows.
            for i in range(8):
                next(xml_file)
            post_date_dict = defaultdict(list)
            post_count = 0
            for line in xml_file:
                if post_count % 10000 == 0:
                    print(post_count)
                post_count += 1
                try:
                    post_info = eTree.fromstring(line)

                except UnicodeDecodeError as ue:
                    encoded_line = line.encode("latin-1", "ignore")
                    post_info = eTree.fromstring(encoded_line)

                except ParseError as pe:
                    print("Parse error occurred " + line)
                    break

                if "OwnerUserId" in post_info.attrib:
                    owner = post_info.attrib["OwnerUserId"]
                else:
                    owner = -99
                post_date_obj = parse(post_info.attrib["CreationDate"])
                year_month = str(post_date_obj.year) + "-" + str(post_date_obj.month)
                if post_info.attrib["PostTypeId"] == "1":
                    post_date_dict[year_month].append((post_info.attrib["PostTypeId"],
                                                       owner,
                                                       post_info.attrib["Tags"],
                                                       post_info.attrib["Id"]))

                elif post_info.attrib["PostTypeId"] == "2":
                    post_date_dict[year_month].append((post_info.attrib["PostTypeId"],
                                                       owner,
                                                       post_info.attrib["ParentId"],
                                                       post_info.attrib["Id"]))

        for year_month, post_list in post_date_dict.items():
            tools.save_pickle(self.folder_path + "Posts/posts_per_month/" + year_month, post_list)


if __name__ == "__main__":
    s_parser = StackParser()
    s_parser.parse_users()
    for yy in range(2008, 2021):
        s_parser.parse_votes(yy)
    s_parser.parse_posts()
