from Tool_Pack import tools
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from datetime import datetime
from operator import itemgetter
import glob
import time


class ScoreCalculator:
    def __init__(self):
        self.start_date_obj = parse("2008-08-01T00:00:00.000")
        self.end_date_obj = parse("2020-12-31T00:00:00.000")
        self.data_path = "path_to_xml_files"
        self.post_date_index = self.create_date_index()

        self.date_to_user_score = dict()
        # Iterate on months to initialize date_to_user_score
        current_date_obj = self.start_date_obj
        m_delta = relativedelta(months=1)
        while current_date_obj < self.end_date_obj:
            self.date_to_user_score[str(current_date_obj.year) + "-" + str(current_date_obj.month)] = dict()
            current_date_obj += m_delta

    def create_date_index(self):
        set_list = list()
        start_date_obj = parse("2008-08-01T00:00:00.000")
        end_date_obj = parse("2020-12-31T00:00:00.000")
        month_delta = relativedelta(months=1)
        while start_date_obj < end_date_obj:
            date_string = str(start_date_obj.year) + "-" + str(start_date_obj.month)
            post_dict = tools.load_pickle(self.data_path + "Posts/posts_per_month/" + date_string)
            month_set = set()
            for post in post_dict:
                month_set.add(post[3])
            set_list.append((date_string, month_set))
            start_date_obj += month_delta
        print("Date index created.")
        print(len(set_list))
        return set_list

    # Creating a new more efficient format of the posts
    def reform_post_lists(self):
        print("In reform post lists.")
        for filepath in glob.iglob(self.data_path + "Posts/posts_per_month/*"):
            post_dict = dict()
            file_name = filepath.split("/")[-1]
            print(file_name)
            post_list = tools.load_pickle(filepath)
            for post in post_list:
                post_dict[int(post[3])] = (post[0], post[1], post[2])
            tools.save_pickle(self.data_path + "pivot_files/reformed_posts/" + file_name, post_dict)
        print("reform post lists done.")

    def reform_votes(self):
        print("In reform votes.")
        current_date_obj = self.start_date_obj
        month_delta = relativedelta(months=1)
        while current_date_obj < self.end_date_obj:
            vote_date = str(current_date_obj.year) + "-" + str(current_date_obj.month)
            c_month_votes = tools.load_pickle(self.data_path + "Votes/votes_per_month/" + vote_date)
            reformed_votes = list()
            counter = 0
            for vote in c_month_votes:
                if counter % 10000 == 0:
                    print((counter / len(c_month_votes) * 100), "%")
                counter += 1
                for date_tuple in self.post_date_index:
                    if vote[1] in date_tuple[1]:
                        split_date = date_tuple[0].split('-')
                        temp_date_obj = datetime(int(split_date[0]), int(split_date[1]), 1)
                        reformed_votes.append((vote[0], vote[1], vote[2], temp_date_obj))
            reformed_votes.sort(key=itemgetter(3))
            tools.save_pickle(self.data_path + "pivot_files/reformed_votes/" + vote_date, reformed_votes)
            current_date_obj += month_delta
        print("Reform votes finished.")

    def get_post_date(self, post_id):
        for date_tuple in self.post_date_index:
            if post_id in date_tuple[1]:
                return date_tuple[0]
        return "no_post"

    def create_date_indexes(self):
        print("In create_date_indexes.")
        current_date_obj = self.start_date_obj
        month_delta = relativedelta(months=1)
        while current_date_obj < self.end_date_obj:
            date_string = str(current_date_obj.year) + "-" + str(current_date_obj.month)
            print(date_string)
            post_dict = tools.load_pickle(self.data_path + "Posts/posts_per_month/" + date_string)
            month_set = set()
            for post in post_dict:
                month_set.add(post[3])
            current_date_obj += month_delta
            tools.save_pickle(self.data_path + "pivot_files/date_to_postid/" + date_string, month_set)
        print("create_date_indexes done.")

    @staticmethod
    def parse_tags(tag_str):
        list_tags = tag_str.split('<')
        clean_list = list()
        for tag in list_tags:
            if len(tag) > 0:
                clean_list.append(tag.replace('>', ''))
        return clean_list

    def working_on_votes(self):
        current_date_obj = self.start_date_obj
        month_delta = relativedelta(months=1)
        while current_date_obj < self.end_date_obj:
            vote_date = str(current_date_obj.year) + "-" + str(current_date_obj.month)
            print(vote_date)
            c_month_votes = tools.load_pickle(self.data_path + "pivot_files/reformed_votes/" + vote_date)
            vote_count = 0
            start_time = time.time()
            # The votes are ordered based on the date of the posts they are placed
            # this way we only need to load each date_to_id_to_post file once per date.
            post_date = "2008-8"
            date_to_id_to_post = tools.load_pickle(self.data_path + "pivot_files/reformed_posts/" + post_date)

            # We will collect the answers with their responding question date and process them
            # with the same approach we did with the answers.
            answer_collection = list()

            for vote in c_month_votes:
                if vote_count % 10000 == 0:
                    print("Percentage: ", vote_count/len(c_month_votes) * 100, "%")
                    print("Execution time", time.time() - start_time)
                    start_time = time.time()
                vote_count += 1
                if str(vote[3].year) + "-" + str(vote[3].month) != post_date:
                    post_date = str(vote[3].year) + "-" + str(vote[3].month)
                    date_to_id_to_post = tools.load_pickle(self.data_path + "pivot_files/reformed_posts/" + post_date)
                post_tuple = date_to_id_to_post[int(vote[1])]
                # if question
                if post_tuple[0] == '1':
                    # if the post is not deleted
                    if post_tuple[1] != -99:
                        # getting a list of the posts tags
                        tag_list = self.parse_tags(post_tuple[2])
                        if post_tuple[1] in self.date_to_user_score[vote_date]:
                            if vote[2] == '2':
                                self.date_to_user_score[vote_date][post_tuple[1]][0] += 10
                                for tag in tag_list:
                                    if tag in self.date_to_user_score[vote_date][post_tuple[1]][1]:
                                        self.date_to_user_score[vote_date][post_tuple[1]][1][tag] += 10
                                    else:
                                        self.date_to_user_score[vote_date][post_tuple[1]][1][tag] = 10
                        else:
                            if vote[2] == '2':
                                temp_tag_dict = dict()
                                for tag in tag_list:
                                    temp_tag_dict[tag] = 10
                                self.date_to_user_score[vote_date][post_tuple[1]] = [10, temp_tag_dict]

                # if answer
                if post_tuple[0] == '2':
                    if post_tuple[1] != -99:
                        question_date = self.get_post_date(post_tuple[2])
                        if question_date != 'no_post':
                            split_date = question_date.split('-')
                            temp_date_obj = datetime(int(split_date[0]), int(split_date[1]), 1)
                            answer_collection.append((post_tuple[0], post_tuple[1], post_tuple[2],
                                                      vote[2], temp_date_obj))

            answer_collection.sort(key=itemgetter(4))
            question_date = "2008-8"
            date_to_id_to_question = tools.load_pickle(self.data_path + "pivot_files/reformed_posts/" + question_date)
            for answer in answer_collection:
                if str(answer[4].year) + "-" + str(answer[4].month) != question_date:
                    question_date = str(answer[4].year) + "-" + str(answer[4].month)
                    date_to_id_to_question = tools.load_pickle(self.data_path + "pivot_files/reformed_posts/"
                                                               + question_date)
                question_tuple = date_to_id_to_question[int(answer[2])]
                tag_list = self.parse_tags(question_tuple[2])
                if answer[1] in self.date_to_user_score[vote_date]:
                    if answer[3] == '1':
                        self.date_to_user_score[vote_date][answer[1]][0] += 15
                        for tag in tag_list:
                            if tag in self.date_to_user_score[vote_date][answer[1]][1]:
                                self.date_to_user_score[vote_date][answer[1]][1][tag] += 15
                            else:
                                self.date_to_user_score[vote_date][answer[1]][1][tag] = 15
                    if answer[3] == '2':
                        self.date_to_user_score[vote_date][answer[1]][0] += 10
                        for tag in tag_list:
                            if tag in self.date_to_user_score[vote_date][answer[1]][1]:
                                self.date_to_user_score[vote_date][answer[1]][1][tag] += 10
                            else:
                                self.date_to_user_score[vote_date][answer[1]][1][tag] = 10
                else:
                    if answer[3] == '1':
                        temp_tag_dict = dict()
                        for tag in tag_list:
                            temp_tag_dict[tag] = 15
                        self.date_to_user_score[vote_date][answer[1]] = [15, temp_tag_dict]
                    if answer[3] == '2':
                        temp_tag_dict = dict()
                        for tag in tag_list:
                            temp_tag_dict[tag] = 10
                        self.date_to_user_score[vote_date][answer[1]] = [10, temp_tag_dict]
            current_date_obj += month_delta
        tools.save_pickle(self.data_path + "pivot_files/month_scores", self.date_to_user_score)


if __name__ == "__main__":
    calculator = ScoreCalculator()
    calculator.reform_post_lists()
    calculator.create_date_indexes()
    calculator.reform_votes()
    calculator.working_on_votes()
