import os

site = []
def generate_file_tree_global(path, depth):
    global site
    filenames_list = os.listdir(path)
    if len(filenames_list) < 1:
        return
    last_filename = filenames_list[-1]

    for item in filenames_list:
        string_list = ["│   " for _ in range(depth - site.__len__())]
        for s in site:
            string_list.insert(s, "    ")
        if item != last_filename:
            string_list.append("├── ")
        else:
            string_list.append("└── ")
            site.append(depth)

        print("".join(string_list) + item)
        new_path = path + '/' + item
        if os.path.isdir(new_path):
            generate_file_tree_global(new_path, depth + 1)
        if item == last_filename:
            site.pop()

if __name__ == '__main__':
    root_path = r'C:\Users\chru\Desktop\Engine5.2.1'
    print(os.path.abspath(root_path))
    generate_file_tree_global(root_path, depth=0)
