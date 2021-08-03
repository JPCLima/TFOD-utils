import argparse

# Initiate argument parser
parser = argparse.ArgumentParser(
    description="Generate a labelmap")

parser.add_argument("-l",
                    "--labels",
                    nargs="+",
                    help="labels of the classes")

parser.add_argument("-p",
                    "--path",
                    default='Tensorflow\\workspace\\annotations\\label_map.pbtxt',
                    help="path of the file")


args = parser.parse_args()


def generate_label_map(labels, path):
    labels_list = [{'name': label, 'id': index + 1} for index, label in enumerate(labels)]

    with open(path, 'w') as f:
        for label in labels_list:
            f.write('item { \n')
            f.write('\tname:\'{}\'\n'.format(label['name']))
            f.write('\tid:{}\n'.format(label['id']))
            f.write('}\n')

def main():
    generate_label_map(args.labels, args.path)

if __name__ == '__main__':
    main()
