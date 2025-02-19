import numpy as np
from collections import defaultdict


class AverageDistortionMetric:

    def __init__(self):
        pass

    def calculate_metric(self, graph_distances, manifold_distances):
        """
        Distortion is computed as:
            distortion(u,v) = |d_s(u,v) - d_g(u,v)| / d_g(u,v)

        :param graph_distances: distances in the graph (b, 1)
        :param manifold_distances: distances in the manifold (b, 1)
        :return: average_distortion: tensor of (1)
        """
        # distortion = torch.div(torch.abs(torch.sub(manifold_distances, graph_distances)), graph_distances)

        if graph_distances.is_cuda:
            manifold_distances = manifold_distances.cpu().numpy().reshape(-1)
            graph_distances = graph_distances.cpu().numpy().reshape(-1)

        distortion = abs(manifold_distances - graph_distances) / graph_distances

        return distortion


class MeanAveragePrecisionMetric:

    def __init__(self, triples):
        """
        :param triples: TensorDataset
        """
        neighbors = defaultdict(set)
        for i in range(len(triples)):
            (src, dst), distance = triples[i][0].tolist(), triples[i][1].tolist()
            if distance == 1:
                neighbors[src].add(dst)
                neighbors[dst].add(src)
        self.neighbors = neighbors

    def calculate_metric(self, distance_matrix):
        """
        Mean average precision as defined in "Learning mixed-curvature representations in products of model spaces".
        Code adapted from https://github.com/dalab/matrix-manifolds/blob/master/graphembed/graphembed/metrics.py#L77
        The complexity is squared in the number of nodes.

        :param distance_matrix: Pairwise distances on the manifold, as an (n,n)-shaped symmetric
                                tensor with zeros on the diagonal.
        """
        ap_scores = []
        for node_id in range(len(distance_matrix)):
            sorted_nodes = np.argsort(distance_matrix[node_id]).tolist()
            neighs = self.neighbors[node_id]
            n_correct = 0.0
            precisions = []
            for i in range(1, len(sorted_nodes)):
                if sorted_nodes[i] in neighs:
                    n_correct += 1
                    precisions.append(n_correct / i)
                    if n_correct == len(neighs):
                        break

            ap_scores.append(np.mean(precisions))

        return np.mean(ap_scores)
