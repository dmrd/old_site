# this script converts your markdown into a production-ready web site

import os, sys, argparse, re, datetime

# get optional command-line arguments
parser = argparse.ArgumentParser("Turn Markdown files into static web sites.")
parser.add_argument('--template', dest='template_file', metavar='template_file', nargs='?', default="post.html", help='post template file')
parser.add_argument('--gfm', dest='gfm', action='store_const', const=True, default=False, help='activate github-flavored markdown')
parser.add_argument('--minify', dest='minify', action='store_const', const=True, default=False, help='activate CSS minification')
parser.add_argument('--prettify', dest='prettify', action='store_const', const=True, default=False, help='activate code syntax highlighting')
parser.add_argument('posts', nargs='*', default=[], help='a list of posts to generate (defaults to all possible posts), specified by the name of the post\'s directory')
args = parser.parse_args()

# gather template file HTML
templateHTML = open(args.template_file, "r").read()

# iterate over all markdown files in this directory and subdirectories

ROOT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
FILENAME_MATCH = re.compile(r'markdown.(txt|md|mdown|markdown)')
FILENAME_DATE = re.compile(r'([0-9]{4})-([0-9]{1,2})-([0-9]{1,2})\.(md|txt|markdown|mdown)$')
META_MATCH = re.compile(r'^meta--(.*)--(.*)$')
CSS_DIRECTORY = ROOT_DIRECTORY + "/production/static/css/"


# a list of all the files in ROOT_DIRECTORY that match FILENAME_MATCH
def post_filter(path, name):
    def valid_filename(s):
        return bool(FILENAME_DATE.match(s)) or bool(FILENAME_MATCH.match(s))
    return ((not args.posts) or (path.split('/')[-1] in args.posts)) and valid_filename(name)

csv_files = [os.path.join(root, name)
             for root, dirs, files in os.walk(ROOT_DIRECTORY)
             for name in files
             if post_filter(root, name)]

# set compilation function
compile_markdown = "ruby utils/gfm.rb %s | pandoc -S -o temp.html" if args.gfm else "pandoc -S -o temp.html %s"
#compile_markdown = "ruby utils/gfm.rb %s | perl utils/markdown.pl > temp.html" if args.gfm else "perl utils/markdown.pl %s > temp.html"

# compress CSS
if args.minify:
    combined_css_path = CSS_DIRECTORY + 'combined.css'
    # delete CSS if already exists
    if os.path.isfile(combined_css_path):
        os.remove(combined_css_path)

    # merge all CSS
    css_files = [os.path.join(root, name) for root, dirs, files in os.walk(CSS_DIRECTORY) for name in files if ".css" in name]
    all_css = ''.join([open(f).read() for f in css_files])

    # compress CSS
    from cssmin import cssmin
    minifed_css = cssmin(all_css)

    # store all CSS in single file
    combined_css = open(combined_css_path, "w+")
    combined_css.write(minifed_css)

# generate blog posts
for file_path in csv_files:

    print("Producing " + file_path)

    # determine the current directory
    pathArray = file_path.split("/")
    del(pathArray[-1])
    directory = "/".join(pathArray)

    sys.stdout.flush()

    # extract metadata from the markdown
    metadata = {}
    with open(file_path, 'r') as f:
        for l in f:
            match = META_MATCH.match(l)
            if match:
                groups = match.groups()
                metadata[groups[0]] = groups[1]
    if 'title' not in metadata:
        # extract the title from the markdown
        with open(file_path, 'r') as f:
            title = f.readline().strip()
        while title[0] == "#":
            title = title[1:]
        metadata['title'] = title.strip()

    if 'date' not in metadata:
        # extract date from file name
        m = FILENAME_DATE.match(file_path.split("/")[-1])
        if m:
            date = datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            fdate = date.strftime("%B %-d, %Y")
        else:
            fdate = ""
        metadata['date'] = fdate

    print("Detected metadata: " + str(metadata))
    # run the converter and output to a temp.html
    os.system(compile_markdown % file_path)

    # now read the output from temp.html and inject into post.html
    tempHTML = open("temp.html", "r").read()

    productionHTML = templateHTML.replace("{{ body }}", tempHTML)
    for k,v in metadata.items():
        # {{ escapes {, so {{{{ -> {{
        productionHTML = productionHTML.replace("{{{{ {key} }}}}".format(key=k), v)

    if args.minify:
        # need to get relative path from HTML file to minified css
        common_prefix = os.path.commonprefix([file_path, combined_css_path])
        relative_path = '../' + os.path.relpath(combined_css_path, common_prefix)
        productionHTML = productionHTML.replace("{{ minified_css }}", relative_path)
    if args.prettify:
        # need to do two passes b/c possible negative lookbehind solution requires fixed-length regex
        productionHTML = productionHTML.replace('<code', '<code class="prettyprint"')
        productionHTML = re.sub(r'(\<\!--\?prettify(.*)\?--\>\n\n\<pre.*\>)<code class="prettyprint"', r'\1<code', productionHTML)

    # write that production output to index.html in original directory
    productionFile = open(directory+"/index.html", "w")
    productionFile.write(productionHTML)

if os.path.exists("temp.html"):
    os.system("rm temp.html")
print("Production complete.")
