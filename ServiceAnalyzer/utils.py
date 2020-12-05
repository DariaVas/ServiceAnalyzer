def read_cvs_file(path):
    num_of_initial_rows = 0
    content = []
    with open(path, 'r') as f:
        for l in f:
            if num_of_initial_rows == 0:
                headers = l
            else:
                content.append(l)
            num_of_initial_rows += 1
    return headers, content, num_of_initial_rows


def generate_test_cvs_file(file_path, source_content, source_headers, num_required_rows):
    rows = 0
    with open(file_path, 'w+') as fout:
        fout.write(source_headers)
        while rows != num_required_rows:
            for r in source_content:
                r = r.strip()
                r = r + '\n'
                if rows == num_required_rows:
                    break
                fout.write(r)
                rows += 1


def convert_string_list_to_int(list_):
    new_list = []
    for item in list_:
        new_list.append(int(item.rstrip()))
    return new_list
