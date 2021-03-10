import csv
import community    
import infomap # https://mapequation.github.io/infomap/
import networkx.algorithms.community as nxcom
from collections import defaultdict
import networkx as nx
from operator import itemgetter
from Tool_Pack import tools


class CommunityAnalyser:

    def __init__(self, year):
        self.year = year
        self.path = "path_to_graph_files"
        self.pivot_path = "path_to_pivot_files"

    def read_edges_csv(self):
        edge_list = list()
        csv_reader = csv.reader(open(self.path + "Relations/" + str(self.year)
                                     + "_users_relations.csv"), delimiter=',', quotechar='"')
        # Skipping header line
        next(csv_reader)
        for row in csv_reader:
            # (source, target, weight)
            edge_list.append((int(row[0]), int(row[1]), float(row[2])))
        return edge_list

    def form_graph(self):
        edges = self.read_edges_csv()
        user_graph = nx.Graph()
        user_graph.add_weighted_edges_from(edges)
        return user_graph

    def community_detection(self, algorithm):
        if algorithm == "Louvain":
            community_dict = defaultdict(list)
            communities = list()
            graph = self.form_graph()
            partition = community.best_partition(graph)
            for node_id, community_id in partition.items():
                community_dict[community_id].append(node_id)
            for com_node_list in community_dict.values():
                communities.append(com_node_list)
            communities = sorted(communities, key=len, reverse=True)
        elif algorithm == "LPA":
            graph = self.form_graph()
            communities = sorted(nxcom.asyn_lpa_communities(graph, weight="weight"),
                                 key=len, reverse=True)
        elif algorithm == "Infomap":
            com_size_threshold = 0.01
            com_nodes = defaultdict(list)
            com_sizes = list()
            big_coms = list()
            infomap_inst = infomap.Infomap("--two-level --undirected --silent")
            network = infomap_inst.network()
            edges = self.read_edges_csv()
            for edge in edges:
                network.addLink(edge[0], edge[1], edge[2])
            infomap_inst.run()
            node_counter = 0
            for node in infomap_inst.iterTree():
                if node.isLeaf():
                    node_counter += 1
                    com_nodes[node.moduleIndex()].append(node.physicalId)
            print(node_counter)
            for com, node_list in com_nodes.items():
                com_sizes.append((com, node_list))
            com_sizes.sort(key=lambda x: len(x[1]), reverse=True)
            # Getting communities that have at least (com_size_threshold)% of the total graph nodes
            com_threshold_size = node_counter * com_size_threshold
            for c_size in com_sizes:
                if len(c_size[1]) > com_threshold_size:
                    big_coms.append(c_size[1])
            tools.save_pickle(self.path + "Communities/" + str(self.year) + "_infomap_coms.pickle", big_coms)
        else:
            print(f"The {algorithm} algorithm is not supported.")
        print("Community detection done.")

    def communities_top_tags(self):
        user_tag_dict = tools.load_pickle(self.pivot_path + str(self.year) + "_normalized")
        communities = tools.load_pickle(self.path + "Communities/" + str(self.year) + "_infomap_coms.pickle")
        tag_scores_list = list()
        for com in communities:
            com_tags_scores_dict = defaultdict(float)
            for user_id in com:
                tag_dict = user_tag_dict[str(user_id)][1]
                for tag, score in tag_dict.items():
                    com_tags_scores_dict[tag] += score
            current_com_list = list(zip(com_tags_scores_dict.keys(), com_tags_scores_dict.values()))
            current_com_list.sort(key=itemgetter(1), reverse=True)
            tag_scores_list.append(current_com_list)
        tools.save_pickle(self.path + "Communities/" + str(self.year) + "_top_tags_per_community.pickle", tag_scores_list)


if __name__ == '__main__':
    for c_year in range(2008, 2021):
        print(c_year)
        analyser = CommunityAnalyser(2020)
        analyser.community_detection("Infomap")
        analyser.communities_top_tags()
