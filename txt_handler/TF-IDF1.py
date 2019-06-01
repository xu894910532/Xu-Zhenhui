# coding=utf-8
import jieba.analyse
from sklearn.feature_extraction.text import *
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

corpus = []  # 文档语料 空格连接

# 读取语料 语料为一个文档
for index in range(375):
    with open('cut_results/poi_%s.txt' % str(index + 1), 'r') as poi_file:
        file_feature = jieba.analyse.textrank(poi_file.read(), topK=30)
        corpus.append('/'.join(file_feature))

vectorizer = CountVectorizer()
transformer = TfidfTransformer()

weight = transformer.fit_transform(vectorizer.fit_transform(corpus))
# print ' '.join(vectorizer.get_feature_names()).encode('utf-8')
# for i in weight[0:10]:
#     print list(i)

pca = PCA(n_components=2)
reduced = pca.fit_transform(weight)

# # 选取K值
# SSE = []
#
# for n_clusters in range(1, 20):
#     clf = KMeans(n_clusters=n_clusters)
#     clf.fit(weight)
#     SSE.append(clf.inertia_)
# X = range(1, 20)
# plt.xlabel('k')
# plt.ylabel('SSE')
# plt.plot(X, SSE, 'o-')
# plt.show()
# print SSE

cluster0_pois = []
cluster1_pois = []
cluster2_pois = []
cluster3_pois = []
cluster4_pois = []

clf = KMeans(n_clusters=5, max_iter=1200)
clf.fit_predict(reduced)
labels = clf.labels_
for index in range(len(reduced)):
    if int(labels[index]) == 0:
        plt.scatter(reduced[index][0], reduced[index][1], color='red')
        cluster0_pois.append(index + 1)
    elif int(labels[index]) == 1:
        plt.scatter(reduced[index][0], reduced[index][1], color='green')
        cluster1_pois.append(index + 1)
    elif int(labels[index]) == 2:
        plt.scatter(reduced[index][0], reduced[index][1], color='blue')
        cluster2_pois.append(index + 1)
    elif int(labels[index]) == 3:
        plt.scatter(reduced[index][0], reduced[index][1], color='orange')
        cluster3_pois.append(index + 1)
    elif int(labels[index]) == 4:
        plt.scatter(reduced[index][0], reduced[index][1], color='black')
        cluster4_pois.append(index + 1)
plt.show()
plt.close()
print '\n----------'
for index in cluster0_pois:
    with open('cut_results/poi_%s.txt' % str(index), 'r') as poi_file:
        poi_info = poi_file.read().split(' ')[0]
        print poi_info,
print '\n----------'
for index in cluster1_pois:
    with open('cut_results/poi_%s.txt' % str(index), 'r') as poi_file:
        poi_info = poi_file.read().split(' ')[0]
        print poi_info,
print '\n----------'
for index in cluster2_pois:
    with open('cut_results/poi_%s.txt' % str(index), 'r') as poi_file:
        poi_info = poi_file.read().split(' ')[0]
        print poi_info,
print '\n----------'
for index in cluster3_pois:
    with open('cut_results/poi_%s.txt' % str(index), 'r') as poi_file:
        poi_info = poi_file.read().split(' ')[0]
        print poi_info,
print '\n----------'
for index in cluster4_pois:
    with open('cut_results/poi_%s.txt' % str(index), 'r') as poi_file:
        poi_info = poi_file.read().split(' ')[0]
        print poi_info,
