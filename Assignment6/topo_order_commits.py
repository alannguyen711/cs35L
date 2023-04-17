import zlib
import os
import sys
import copy
from collections import deque


def topo_order_commits():
    path = get_git_dir()
    path = path + "/.git/"
    branches = retrieve_branches(path)
    commit_info, root = find_commits(path, branches)
    sorted_commits = topological_sort(commit_info, root)
    initial = False

    #print function to output commit info
    print_output(initial, sorted_commits, commit_info, root) 


def get_git_dir(d="."):
    # function to get directory for git directory
    while(os.path.abspath(d) != "/"):
        for dir in os.listdir(d):
            if os.path.isdir(os.path.join(d, dir)) and dir == ".git":
                return os.path.abspath(d)
        d = "../" + d
    sys.stderr.write("Not inside a Git repository\n")
    sys.exit(1)


def retrieve_branches(path):
    branch_path = path + "refs/heads/"
    branch_code = dict()
    if not os.path.isdir(branch_path):
        sys.stderr.write("Not a directory\n")
        sys.exit(1)
    for root, dirs, files in os.walk(branch_path):
        if files:
	        for f in files:
	            hash = open(os.path.join(root, f), 'rb').read().decode("latin-1")
	            hash = hash.strip('\n')
	            if branch_code.get(hash) is None:
	                branch_code[hash] = list()
	            meta = os.path.join(root, f)[len(branch_path):]
	            branch_code[hash].append(meta)
    return branch_code


def find_commits(path, branch_code):
    commit_dict = dict()
    root_commits = set()
    obj_path = path + "objects/"
    for hash in branch_code:
        if commit_dict.get(hash) is not None:
            commit_dict[hash].branches = branch_code[hash]
            continue
        commit_dict[hash] = CommitNode(hash, branch_code[hash])
        sorted_object = depth_first(obj_path, hash, commit_dict)
        root_commits = root_commits.union(sorted_object)
    root_commits = sorted(root_commits)
    return commit_dict, root_commits


def topological_sort(commit_meta, root_commits):
    # sorts commits topologically
    out = list()
    visited = dict()
    c_stack = list(root_commits.copy())
    while len(c_stack) > 0:
        top_val = c_stack[-1]
        visited[top_val] = "seen"
        cur_children = [child for child in commit_meta[top_val].children if visited.get(child) is None]
        if len(cur_children) == 0:
            pop_val = c_stack.pop()
            out.append(pop_val)
            continue
        c_stack.append(cur_children[0])
    return out


def depth_first(path, hash, input_commit):
    # function to perform depth first search
    root_commits = set()
    comm_stack = [input_commit[hash]]
    while len(comm_stack) > 0:
        pop_val = comm_stack.pop()
        pop_val.parents = get_parents(path, pop_val.commit_hash)
        if len(pop_val.parents) == 0:
            root_commits.add(pop_val.commit_hash)
            continue
        for p_hash in pop_val.parents:
            if input_commit.get(p_hash) is not None:
                p_node = input_commit[p_hash]
                p_node.children.add(pop_val.commit_hash)
                continue
            input_commit[p_hash] = CommitNode(p_hash)
            p_node = input_commit[p_hash]
            p_node.children.add(pop_val.commit_hash)
            comm_stack.append(p_node)
    return root_commits


def get_parents(obj_path, hash):
    # retrieves parents
    path = obj_path + hash[:2] + "/" + hash[2:]
    parent_set = set()
    if not os.path.isfile(path):
        sys.stderr.write("No object for hash: " + hash + "\n")
        sys.exit(1)
    obj = open(path, 'rb').read() # TIMEOUT
    obj = zlib.decompress(obj).decode("latin-1")
    obj = obj.replace("\n", " ")

    split = obj.split(" ")

    i = 0
    while split[i] != "author" and i < len(split):
        if split[i-1] == "parent":
            parent_set.add(split[i])
        i += 1
    parent_set = sorted(parent_set)
    return parent_set


def print_output(move_next, sorted_commits, commit_info, root_commits):
    # print function
    for i in range(len(sorted_commits)):
        committed = sorted_commits[i]
        if i < (len(sorted_commits) - 1):
            next_com = sorted_commits[i+1]
        if move_next:
            print("=", end="")
            to_print = commit_info[committed].children
            print(*to_print)
            move_next = False
        if len(commit_info[committed].branches) == 0:
            print(committed)
        else:
            print(committed + " ", end="")
            to_print = sorted(commit_info[committed].branches)
            print(*to_print)
        if next_com not in commit_info[committed].parents and i < (len(sorted_commits) - 1):
            to_print = commit_info[committed].parents
            print(*to_print, end="")
            print("=\n")
            move_next = True

class CommitNode:
    #given class from assignment 6 page
    def __init__(self, commit_hash, branches=[]):
        """
        :type commit_hash: str
        :type branches: set
        """
        self.commit_hash = commit_hash
        self.branches = branches
        self.parents = set()
        self.children = set()

    def __str__(self):
        return 'commit_hash: {self.commit_hash}, branches: {self.branches}'.format(self=self)

    def __repr__(self):
        return 'CommitNode<commit_hash: {self.commit_hash}, branches: {self.branches}>'.format(self=self)


# main function
if __name__ == '__main__':
    topo_order_commits()

# ran strace to verify that my implementation does not use other commands, see topo-test.tr.gz file