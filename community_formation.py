import numpy as np
from wordcloud import WordCloud
from PIL import Image
from Tool_Pack import tools


class CommunityCloud:

    def __init__(self):
        self.path = "/home/iraklis/PycharmProjects/SO_New/SRC3/Revisions/I_O/"
        self.all_com_names = set()
        self.color_dict = {'C/C++ Developers': "#ff5793", 'PHP Developers': "#91cda2", 'Python Developers': "#00996d",
                           'Ruby Developers': "#e2bd6a", 'Android Developers': "#2a4b67", 'Mysql Developers': "#00deeb",
                           'Database Developers': "#97c8e6", 'C Developers': "#b44806", 'Version Control': "#8c58a6",
                           'Javascript back end': "#ff5053", 'Apache-Flex Developers': "#c7a6ac",
                           'Windows Developers': "#68f4d2", 'Apple Developers': "#00c4ff",
                           'Scala Developers': "#962f4b", 'R Developers': "#f9a200", 'Microsoft asp.net': "#afc400",
                           'Java Developers': "#ff7b00", 'Unix/Linux Developers': "#63b939",
                           'Perl Developers': "#602f4b", 'Language Agnostic': "#008198",
                           'Development Operations': "#402f2b", 'asp.net': "#afc400", 'Angular Developers': "#39e200",
                           'Javascript Developers': "#ff7aff", 'Flutter Developers': "#ff7a11"}

    def gather_all_names(self):
        for year in range(2008, 2021):
            annotated_coms = tools.load_pickle(self.path + "Communities0/" + str(year) +
                                               "_annotated_communites.pickle")
            for com in annotated_coms:
                self.all_com_names.add(com)
        print()

    def so_clouds(self, year):
        mask = np.array(
            Image.open("/home/iraklis/Desktop/StackOverflow/Media/Images/WordClouds/proper_circle.png"))
        anno_coms = tools.load_pickle(self.path + "Communities0/" + str(year) + "_annotated_communites.pickle")
        tags = tools.load_pickle(self.path + "Communities0/" + str(year) + "_top_tags_per_community.pickle")

        input_dict = self.convert_to_list_of_dict(tags)
        list_of_colors = self.choose_colors(anno_coms)

        for idx, com in enumerate(anno_coms):
            wc = WordCloud(background_color=list_of_colors[idx], mask=mask, max_words=60, prefer_horizontal=1,
                           contour_width=0.1, collocations=False, margin=1,  width=660, height=660,
                           color_func=lambda *args, **kwargs: (0, 0, 0))
            wc.generate_from_frequencies(input_dict[idx])
            wc.to_file(self.path + "Word_Clouds/" + str(year) + "/" + com.replace('/', '') + ".png")

    @staticmethod
    def convert_to_list_of_dict(tuple_lists):
        dict_list = list()
        for t_list in tuple_lists:
            temp_dict = dict()
            for c_tuple in t_list[:60]:
                temp_dict[c_tuple[0]] = c_tuple[1]
            dict_list.append(temp_dict)
        return dict_list

    def choose_colors(self, anno_list):
        c_list = list()
        for com in anno_list:
            hex_c = self.color_dict[com].strip('#')
            # converting hex color to RGB
            rgb_c = tuple(int(hex_c[i:i + 2], 16) for i in (0, 2, 4))
            c_list.append(rgb_c)
        return c_list


if __name__ == "__main__":
    cloud = CommunityCloud()
    cloud.gather_all_names()
    for year in range(2018, 2021):
        cloud.so_clouds(year)
