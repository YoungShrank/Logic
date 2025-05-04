class ListAlgorithms:
    @staticmethod
    def get_seg_indice(seg_lens: list[int], elem_indice: list[int]):
        """
        已知元素索引，求所在片段索引
        - seg_lens: 片段长度列表
        - elem_indice: 元素索引列表，升序
        """
        seg_indice = []
        seg_index = 0
        seg_start = 0
        for i in elem_indice:
            while (seg_index < len(seg_lens)
                    and not (seg_start <= i and i < seg_start + seg_lens[seg_index])) :
                seg_start += seg_lens[seg_index]
                seg_index += 1
            if seg_index < len(seg_lens):
                seg_indice.append(seg_index)
            else:
                seg_indice.append(-1)
        return seg_indice
    @staticmethod
    def seg_intersect(a_start: int, a_end: int, b_start: int, b_end: int):
        """
        区间交集
        - （a_start, a_end）, （b_start, b_end）: 区间
        """
        if a_end < b_start or a_start > b_end:
            return []
        else:
            return [max(a_start, b_start), min(a_end, b_end)]
    
    @staticmethod
    def map_sublist(origin: list, predicate = lambda x: True):
        """
        获得子列表以及索引映射
        - origin: 原始列表
        - predicate: 断言函数，返回True则保留，返回False则删除
        # return
        - sub_list: 子列表
        - origin2sub: 原始索引到子列表索引的映射
        - sub2origin: 子列表索引到原始索引的映射
        """
        origin2sub = {}
        sub2origin = {}
        sub_list = []
        for i, x in enumerate(origin):
            if predicate(x):
                origin2sub[i] = len(sub_list)
                sub2origin[len(sub_list)] = i
                sub_list.append(x)
        return sub_list, origin2sub, sub2origin

    @staticmethod
    def seg_index_to_item_index(seg_lens: list[int], seg_index: int, inner_index: int):
        """
        片段索引转元素索引
        - seg_lens: 片段长度列表
        - seg_index: 片段索引
        - inner_index: 片段内索引
        """
        pre_sum = ListAlgorithms.get_pre_sum(seg_lens)
        item_index = (0 if seg_index == 0 else pre_sum[seg_index -1]) + inner_index
        return item_index
    
    def item_index_to_seg_index(seg_lens: list[int], item_index: int):
        """
        元素索引转片段索引 
        i ∈ [pre_s[i - 1], pre_s[i])
        - seg_lens: 片段长度列表
        - item_index: 元素索引
        """
        pre_sum = ListAlgorithms.get_pre_sum(seg_lens)
        seg_index = 0
        while seg_index < len(pre_sum) and item_index >= pre_sum[seg_index]:
            seg_index += 1
        assert seg_index <= len(pre_sum)
        return seg_index, item_index - (pre_sum[seg_index - 1] if seg_index > 0 else 0)
    
    @staticmethod
    def get_pre_sum(l: list[int]):
        """
        前缀和
        """
        pre_sum = [0] * len(l)
        pre_sum[0] = l[0]
        for i in range(1, len(l)):
            pre_sum[i] = pre_sum[i - 1] + l[i]
        print(pre_sum)
        return pre_sum

if __name__ == '__main__':
    result = ListAlgorithms.get_seg_indice([1, 2, 3, 4, 5], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    print([0, 1, 1, 2, 2, 2, 3, 3, 3, 3, 4] == result)
    result = ListAlgorithms.map_sublist([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], lambda x: x % 2 == 0)
    print(result)

    # 测试 片段索引转元素索引
    print(ListAlgorithms.seg_index_to_item_index([1, 2, 3, 4, 5], 2, 2) == 5)
    # 测试 前缀和
    print(ListAlgorithms.get_pre_sum([1, 2, 3, 4, 5]) == [ 1, 3, 6, 10, 15])

    # 测试 元素索引转片段索引
    print(ListAlgorithms.item_index_to_seg_index([1, 2, 3, 4, 5], 5) == (2, 2))
