import re

class Node:
    def __init__(self, tikz_str):
        match = re.match(r"\s*\\node \[(.+)\] \((.+?)\) at \((.+?)\) \{(.*?)\};", tikz_str)
        if not match:
            raise Exception("Illegal Node:", tikz_str)
        styles, self.name, self.coord, self.label = match.groups()
        self.extra_styles = {k:v for style in styles.split(", ") for (k,v) in [style.split("=")]}
        self.style = self.extra_styles.pop("style").replace(" ", "_")
        if self.style == 'none':
            self.style = 'none_'
        
    def to_cetz(self):
        emit = []
        if self.style == 'h_gate':
            emit.append(f'{self.style}(({self.coord}), (rel: (0.5, 0.5)), name: "{self.name}")')
        else:
            emit.append(f'{self.style}(({self.coord}), name: "{self.name}")')
        if len(self.label) > 0:
            emit.append(f'content("{self.name}", [{clean_math_exp(self.label)}])')
        return emit
        
def clean_math_exp(exp):
    return exp.replace("\\", "")
    
class Edge:
    def __init__(self, tikz_str):
        match = re.match(r"\s*\\draw(?: \[(.+)\])? \((.+?)(?:.center)?\) to \((.+?)(?:.center)?\);", tikz_str)
        if not match:
            raise Exception("Illegal Edge:", tikz_str)
        self.styles, self.start, self.end = match.groups()

    def to_cetz(self):
        return [f'line(("{self.start}.center"), ("{self.end}.center"))']

def parser(file):
    nodes = []
    edges = []
    with open(file, 'r') as f:
        for line in f.readlines():
            node_match = re.match(r"\s*\\node", line)
            edge_match = re.match(r"\s*\\draw", line)
            ignore_match = re.match(r"\s*\\(?:begin|end)", line)
            if ignore_match:
                pass
            elif node_match:
                nodes.append(Node(line))
            elif edge_match:
                edges.append(Edge(line))
            else:
                raise Exception("Illegal line:", line)
    return nodes, edges

PACKAGE_FILE = '@preview/cetz:0.2.2'
STY_FILE = "cetzsty.typ"

def emmitter(ast, file):
    nodes, edges = ast
    with open(file, 'w') as f:
        f.write(f'#import "{STY_FILE}": *\n\n')
        f.write(f'#cetz.canvas({{\n')
        for ele in nodes:
            emit = ele.to_cetz()
            f.writelines('\t' + em + '\n' for em in emit)
        f.write(f'on-layer(-1, {{\n')
        for ele in edges:
            emit = ele.to_cetz()
            f.writelines('\t' + em + '\n' for em in emit)
        f.write('})\n')
        f.write('})')

def tikz2cetz(in_file, out_file):
    ast = parser(in_file)
    emmitter(ast, out_file)


if __name__ == "__main__":
    in_file = "test/t1.tikz"
    out_file = "test/out.typ"
    tikz2cetz(in_file, out_file)