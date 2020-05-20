import rcssmin
import rjsmin
import sass

"""
This script does 3 things:
    - Compiles scss to css
    - Minifies css
    - Minifies JavaScript
"""

# Map scss source files to css destination files
sass_map = {"static/css/screen.scss": "static/css/screen.css"}

# Map un-minified css source files to minified css destination files
css_map = {"static/css/screen.css": "static/css/screen.min.css"}

# Map un-minified JavaScript source files to minified JavaScript destination files
js_map = {"static/javascript/app.js": "static/javascript/app.min.js"}


def compile_sass_to_css(sass_map):

    print("Compiling scss to css:")

    for source, dest in sass_map.items():
        with open(dest, "w") as outfile:
            outfile.write(sass.compile(filename=source))
        print(f"{source} compiled to {dest}")


def minify_css(css_map):

    print("Minifying css files:")

    for source, dest in css_map.items():
        with open(source, "r") as infile:
            with open(dest, "w") as outfile:
                outfile.write(rcssmin.cssmin(infile.read()))
        print(f"{source} minified to {dest}")


def minify_javascript(js_map):

    print("Minifying JavaScript files:")

    for source, dest in js_map.items():
        with open(source, "r") as infile:
            with open(dest, "w") as outfile:
                outfile.write(rjsmin.jsmin(infile.read()))
        print(f"{source} minified to {dest}")


if __name__ == "__main__":
    print()
    print("Starting runner")
    print("--------------------")
    compile_sass_to_css(sass_map)
    print("--------------------")
    minify_css(css_map)
    print("--------------------")
    minify_javascript(js_map)
    print("--------------------")
    print("Done")
    print()