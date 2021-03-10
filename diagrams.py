import numpy as np
import chart_studio.plotly as py
import chart_studio
import csv
import pandas as pd
from Tool_Pack import tools
import plotly.graph_objects as go
from collections import defaultdict
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.ticker as mtick


class CommunityPlots:

    def __init__(self):
        self.path = "path_to_community_files"
        self.all_dates = ["2008", "2009", "2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018",
                          "2019", "2020"]
        self.display_coms = {"Big": ["PHP Developers", "Python Developers", "Apple Developers", "Microsoft asp.net",
                                      "Javascript Developers", "Java Developers", "C/C++ Developers",
                                      "Android Developers"],
                             "Small": ["Angular Developers", "C Developers", "R Developers",
                                        "Unix/Linux Developers", "Ruby Developers", "Database Developers",
                                        "Version Control"]}
        self.color_dict = {'C/C++ Developers': "#ff5793", 'PHP Developers': "#91cda2", 'Python Developers': "#00996d",
                           'Ruby Developers': "#e2bd6a", 'Android Developers': "#2a4b67", 'Mysql Developers': "#00deeb",
                           'Database Developers': "#97c8e6", 'C Developers': "#b44806", 'Version Control': "#8c58a6",
                           'Javascript back end': "#ff5053", 'Apple Developers': "#00c4ff", 'R Developers': "#f9a200", 'Microsoft asp.net': "#afc400",
                           'Java Developers': "#ff7b00", 'Unix/Linux Developers': "#63b939", 'Language Agnostic': "#008198",
                           'Angular Developers': "#39e200", 'Javascript Developers': "#ff7aff"}

        self.start_date_obj = parse("2008-08-01T00:00:00.000")
        self.end_date_obj = parse("2021-01-01T00:00:00.000")

    def overall(self):
        # Calculating the number of users/nodes of each community
        com_sizes = dict()
        percentage_list = list()
        for idx, c_date in enumerate(self.all_dates[:-1]):
            prev_nodes = set()
            next_nodes = set()

            com_nodes_1 = tools.load_pickle(self.path + c_date + "_infomap_coms.pickle")
            com_names_1 = tools.load_pickle(self.path + c_date + "_annotated_communites.pickle")
            com_nodes_2 = tools.load_pickle(self.path + self.all_dates[idx+1] + "_infomap_coms.pickle")
            com_names_2 = tools.load_pickle(self.path + self.all_dates[idx+1] + "_annotated_communites.pickle")

            for node_list in com_nodes_1:
                for node in node_list:
                    prev_nodes.add(node)
            for node_list in com_nodes_2:
                for node in node_list:
                    next_nodes.add(node)
            new_users = next_nodes - prev_nodes
            percentage_list.append(len(new_users)/len(next_nodes))
        print(np.mean(percentage_list))

    def community_timeseries(self, com_category, format):
        # date for community based time series
        s_date_obj = parse("2008-01-01T00:00:00.000")
        e_date_obj = parse("2021-01-01T00:00:00.000")
        m_delta = relativedelta(years=1)
        date_strings = list()
        all_coms = set()
        community_timeseries_dict = dict()

        current_date_obj = s_date_obj
        while current_date_obj < e_date_obj:
            date_strings.append(current_date_obj)
            current_date_obj += m_delta
        m_dates = matplotlib.dates.date2num(date_strings)

        # gathering community names
        for c_year in self.all_dates:
            annotated = tools.load_pickle(self.path + c_year + "_annotated_communites.pickle")
            for com in annotated:
                all_coms.add(com)
        for com in all_coms:
            community_timeseries_dict[com] = [0] * 13
        for idx, year in enumerate(self.all_dates):
            total_nodes = 0
            com_nodes = tools.load_pickle(self.path + year + "_infomap_coms.pickle")
            for com in com_nodes:
                total_nodes += len(com)
            annotated = tools.load_pickle(self.path + year + "_annotated_communites.pickle")
            for com, com_name in zip(com_nodes, annotated):
                community_timeseries_dict[com_name][idx] = len(com) / total_nodes

        for com in self.display_coms[com_category]:
            plt.plot_date(m_dates, community_timeseries_dict[com], 'b-', color=self.color_dict[com], label=com)

            plt.xlabel('Date')
            plt.ylabel('Percentage of Users')

            plt.title("Community Sizes per Year")
            plt.xticks(rotation=45)

        # defining the limits of an axes
        axes = plt.gca()
        axes.set_ylim([0, 0.41])
        axes.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
        plt.legend()
        plt.savefig(self.path + "p_usrs_" + com_category + "." + format, bbox_inches='tight', format=format, dpi=300)

    def timeseries_plots(self):
        # tag_string = ["android", "ios", "windows", "linux", "unix"]
        # tag_string = ["c++", "c", "python", "java", "r", "ruby", "javascript", "php", "c#"]
        tag_string = ["reactjs", "ruby-on-rails", "asp.net", "angular", "angularjs", "django", "vue.js",
                      "laravel", "spring", "flask"]
        date_strings = list()
        tag_dict = tools.load_pickle("/home/iraklis/PycharmProjects/SO_New/SRC3/Revisions/I_O/Scores/"
                                     "tag_timeseries.pickle")
        default_colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown',
                          'tab:pink', 'tab:gray', 'tab:olive', 'tab:cyan', 'fuchsia', 'black']

        # Create a list of the date strings
        current_date_obj = self.start_date_obj
        month_delta = relativedelta(months=1)
        while current_date_obj < self.end_date_obj:
            date_strings.append(current_date_obj)
            current_date_obj += month_delta
        m_dates = matplotlib.dates.date2num(date_strings)

        for idx, tag in enumerate(tag_string):
            plt.plot_date(m_dates, tag_dict[tag], 'b-', color=default_colors[idx], label=tag)

        plt.xlabel('Date')
        plt.ylabel('Vote Score')

        plt.title("Web Frameworks")
        # plt.title("Programming Languages")
        # plt.title("Operating Systems")
        plt.legend()
        plt.xticks(rotation=45)

        plt.savefig(self.path + "/web_frameworks.png", bbox_inches='tight',
                    format="png", dpi=300)

    def active_users(self):
        start_date_obj = parse("2008-08-01T00:00:00.000")
        end_date_obj = parse("2021-01-01T00:00:00.000")
        m_delta = relativedelta(months=1)
        date_strings = list()
        questions_rec = list()
        answer_rec = list()
        post_users_rec = list()
        score_users_rec = list()
        year_users_dict = dict()

        # creating the dates for the plot
        current_date_obj = start_date_obj
        while current_date_obj < end_date_obj:
            date_strings.append(current_date_obj)
            current_date_obj += m_delta
        m_dates = matplotlib.dates.date2num(date_strings)

        while start_date_obj < end_date_obj:
            year_month_str = str(start_date_obj.year) + "-" + str(start_date_obj.month)
            # the score and tags for each user(uid) for every month
            month_user_scores = tools.load_pickle(self.path + "Month_Analysis/Scores/" + year_month_str)
            month_posts = tools.load_pickle(self.path + "Month_Analysis/Posts/" + year_month_str)
            m_questions = 0
            m_answers = 0
            m_active_users = set()
            for record in month_posts:
                if record[0] == '1':
                    m_questions += 1
                if record[0] == '2':
                    m_answers += 1
                m_active_users.add(record[1])
            questions_rec.append(m_questions)
            answer_rec.append(m_answers)
            post_users_rec.append(len(m_active_users))
            score_users_rec.append(len(month_user_scores))
            if str(start_date_obj.year) in year_users_dict:
                year_users_dict[str(start_date_obj.year)] = \
                    year_users_dict[str(start_date_obj.year)].union(m_active_users)
            else:
                year_users_dict[str(start_date_obj.year)] = m_active_users

            start_date_obj += m_delta

        tools.save_pickle(self.path + "year_active_users", year_users_dict)

        fig, ax1 = plt.subplots()
        color = '#000000'
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Number of Posts', color=color)
        ax1.plot_date(m_dates, questions_rec, 'None', color="tab:red", label="Users made a Post")
        ax1.plot_date(m_dates, questions_rec, 'None', color="tab:orange", label="Users received Score")
        ax1.plot_date(m_dates, questions_rec, 'b-', color="tab:blue", label="Questions")
        ax1.plot_date(m_dates, answer_rec, 'b-', color="tab:green", label="Answers")
        ax1.tick_params(axis='y', labelcolor=color)
        plt.legend()
        axes = plt.gca()
        axes.set_ylim([0, 330000])
        ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

        color = 'tab:red'
        ax2.set_ylabel('Active Users', color=color)  # we already handled the x-label with ax1
        ax2.plot_date(m_dates, post_users_rec, 'b-', color="tab:red", label="Users made a Post")
        ax2.plot_date(m_dates, score_users_rec, 'b-', color="tab:orange", label="Users received Score")
        axes = plt.gca()
        axes.set_ylim([0, 440000])
        ax2.tick_params(axis='y', labelcolor=color)

        fig.tight_layout()  # otherwise the right y-label is slightly clipped

        plt.title("Posts and Active Users per Month")
        plt.xticks(rotation=45)

        plt.savefig(self.path + "users.png"
                    , bbox_inches='tight', format="png", dpi=300)

class TagMonitor:
    def __init__(self):
        self.start_date_obj = parse("2020-01-01T00:00:00.000")
        self.end_date_obj = parse("2021-01-01T00:00:00.000")
        self.score_path = "path_to_score_files"

        self.month_tag_scores = dict()

    def process_scores(self):
        month_delta = relativedelta(months=1)
        current_date_obj = self.start_date_obj
        while current_date_obj < self.end_date_obj:
            date_string = str(current_date_obj.year) + "-" + str(current_date_obj.month)
            print(date_string)
            score_dict = tools.load_pickle(self.score_path + date_string)
            self.month_tag_scores[date_string] = self.slot_score(score_dict)

            current_date_obj += month_delta
        tools.save_pickle(self.score_path + "month_tag_scores", self.month_tag_scores)

    @staticmethod
    def slot_score(t_scores):
        time_slot_tag_score = dict()
        for user_id, user_tags in t_scores.items():
            for tag, score in user_tags[1].items():
                if tag in time_slot_tag_score:
                    time_slot_tag_score[tag] += score
                else:
                    time_slot_tag_score[tag] = score
        return time_slot_tag_score



if __name__ == "__main__":
    com_plots = CommunityPlots()
    tag_plots = TagMonitor()
    com_plots.overall()
    com_plots.community_timeseries("Big", "eps")
    com_plots.timeseries_plots()
    tag_plots.process_scores()



