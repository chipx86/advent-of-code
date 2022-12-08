#!/usr/bin/env python3
#
# This is the same information as task1.py:
#
# For this solution, I went with a full filesystem model, and the very
# basics of a command model approach (though the latter is very basic and
# tailored for these needs).
#
# The filesystem model consists of a `BaseNode` class, which represents a
# node in a filesystem. `DirNode` subclasses that to track children and to
# compute its size from the sum of the childrens' sizes (recursively if
# needed). `FileNode` tracks a file with a set size.
#
# The command parser stores the current command line, then grabs all
# input, and finally feeds it all back into a command handler. The commadn
# handler can then analyze that to figure out what filesystem operations
# to conduct behind the scenes. (This feels a little backwards from
# implementing actual command line support, since the command handlers are
# parsing results, not emitting them).
#
# I went overboard with the filesystem operations. I have path
# normalization built-in (allowing for crazy things like
# `/foo/../bar/.//foobar`), and let commands like `cd` take such paths.
# Might be useful if we ever circle back to this task.
#
# There are some optimizations in here, for memory and runtime performance.
#
# The input is calculated line-by-line, and we only store the minimum amount
# of data necessary.
#
# Dynamic node size calculations for directories uses a @cached_property, so
# that a second request for the size just returns a cached value.


from functools import cached_property


class BaseNode:
    def __init__(self, *, name, parent=None):
        self.name = name
        self.parent = parent

    # The following methods are completely for debugging and not necessary
    # for this task.
    @cached_property
    def full_path(self):
        if self.parent:
            return '%s/%s' % (self.parent.full_path, self.name)
        else:
            return self.name

    def serialize(self):
        return {
            'name': self.name,
            'size': self.size,
        }


class DirNode(BaseNode):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.children = {}

    def add_child(self, node):
        node.parent = self
        self.children[node.name] = node

    def serialize(self):
        return dict({
            'children': [
                child.serialize()
                for child in self.children.values()
            ],
        }, **super().serialize())

    @cached_property
    def size(self):
        # Recursively calculate the size for the parent.
        return sum(
            child.size
            for child in self.children.values()
        )


class FileNode(BaseNode):
    def __init__(self, *, size=None, **kwargs):
        super().__init__(**kwargs)

        self.size = size


def get_or_create_node(*, path, node_type, **defaults):
    if path.startswith('/'):
        cur_node = root
    else:
        cur_node = cwd

    start_node = cur_node

    parts = path.split('/')

    # Perform path normalization. We'll handle things totally unnecessary
    # for this task like "." and redundant slashes (e.g., "///") in paths.
    #
    # Path normalization also constructs the tree. We've started with a parent
    # node, and we'll keep setting that as we navigate up/down the tree to
    # build our path.
    for i, part in enumerate(parts, start=1):
        if not part:
            continue

        if part == '..':
            cur_node = cur_node.parent
        elif part != '.':
            assert hasattr(cur_node, 'children')

            try:
                cur_node = cur_node.children[part]
            except KeyError:
                if i == len(parts):
                    # We're at the leaf of this path. We can now construct
                    # the node the caller wants.
                    new_node = node_type(name=part, **defaults)
                else:
                    new_node = DirNode(name=part)

                cur_node.add_child(new_node)
                cur_node = new_node

    return cur_node


def walk_dirs(parent=None):
    if parent is None:
        parent = root

    yield parent

    for child in parent.children.values():
        if isinstance(child, DirNode):
            yield from walk_dirs(child)


def on_handle_cd(path, **kwargs):
    global cwd

    # Create the resulting directory node, and then set it as the new current
    # directory.
    cwd = get_or_create_node(path=path,
                             node_type=DirNode)


def on_handle_ls(*, output=[]):
    # Go through the output and create any nodes we find, relative to the
    # current directory. If it's a "dir", we create a directory node.
    # Otherwise, create a a file node and set its size.
    for line in output:
        line = line.strip()
        parts = line.split(' ', 1)
        pathname = parts[1]

        if parts[0] == 'dir':
            get_or_create_node(path=pathname,
                               node_type=DirNode)
        else:
            get_or_create_node(path=pathname,
                               node_type=FileNode,
                               size=int(parts[0]))


COMMANDS = {
    'cd': on_handle_cd,
    'ls': on_handle_ls,
}


cwd = None
root = DirNode(name='')


with open('input', 'r') as fp:
    cur_cmdline = None
    cwd = None
    cmd_output = []

    def run_cur_command():
        global cmd_output
        global cur_cmdline

        COMMANDS[cur_cmdline[0]](*cur_cmdline[1:],
                                 output=cmd_output)
        cmd_output = []
        cur_cmdline = []

    # For our command parser, we're going to find any new commands being run,
    # parse the command line, store it, and then grab any output.
    #
    # Once we find a new command, we "execute" the stored command and pass
    # the output, then reset state. The same happens once we've finished the
    # full input stream.
    for line in fp.readlines():
        if line.startswith('$ '):
            # This is a command.
            if cur_cmdline is not None:
                run_cur_command()

            cur_cmdline = line[2:].split()
        else:
            # This is output for a current command.
            cmd_output.append(line)

    run_cur_command()


# We need to figure out the smallest directory we can delete that will give
# us the space back that we need.
#
# We know we have 70MB of space, and need 30MB free.
#
# So first, we need to figure out how much space is currently available. We
# determine this by getting the total space of the drive and subtracting the
# used space (which we know via the root directory's recursive size).
#
# We can then walk directories, considering only those that, if deleted, get
# us over that threshold. The smallest of these candidates is our winner.
TOTAL_SPACE = 70_000_000
SPACE_NEEDED = 30_000_000

space_available = TOTAL_SPACE - root.size
smallest_candidate = None

for node in walk_dirs():
    if space_available + node.size >= SPACE_NEEDED:
        if smallest_candidate is None or node.size < smallest_candidate.size:
            smallest_candidate = node


print(f'Smallest candidate dir = %s (size=%d)' % (smallest_candidate.full_path,
                                                  smallest_candidate.size))
