# encoding=utf-8
import jieba

# 加载自定义词表
jieba.load_userdict('small_dict.txt')


# 创建停用词list
def get_stop_words(file_path='stop_words.txt'):
    return [line.strip() for line in open(file_path, 'r').readlines()]


for index in range(375):
    with open('poi_files/poi_%s.txt' % str(index + 1), 'r') as poi_file:
        poi_info = poi_file.read()
        seg_list = jieba.cut(poi_info.strip(), cut_all=False)  # 精确模式
        result = []
        for seg in seg_list:
            seg = seg.encode('utf-8')
            if seg not in get_stop_words() and seg:
                result.append(seg)
        output = '/'.join(result)  # 空格拼接
        with open('cut_results/poi_%s.txt' % str(index + 1), 'w') as poi_result:
            poi_result.write(output)
