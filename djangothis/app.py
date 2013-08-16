import os, sys, yaml
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

from importd import d

__version__ = '0.2'

def dotslash(pth):
    return os.path.join(os.getcwd(), pth)

sys.path.append(os.getcwd())

d(
    DEBUG=True,
    TEMPLATE_DIRS=[os.getcwd()],
    STATICFILES_DIRS=[dotslash("static")],
    INSTALLED_APPS=["djangothis"],
)

try:
    import views
except ImportError:
    pass
else:
    views

try:
    import forms
except ImportError:
    pass
else:
    forms

from django.contrib.staticfiles.views import serve
from fhurl import JSONResponse

@d(".*")
def handle(request):
    path = request.path[1:]

    if path == "favicon.ico":
        return serve(request, path)

    if path.startswith("static"):
        return serve(request, request.path[len("/static/"):])

    if path == "" or path.endswith("/"):
        path = path + "index.html"

    if os.path.exists(dotslash(path)) and os.path.isfile(dotslash(path)):
        return path

    try:
        ajax = yaml.load(file(dotslash("ajax.yaml")), Loader=Loader)
    except Exception:
        pass
    else:
        if ajax:
            if request.GET:
                path = request.path + "?" + request.META["QUERY_STRING"]
                # TODO: make it immune to order of GET params
                if path in ajax:
                    return JSONResponse(ajax[path])
            if request.path in ajax:
                return JSONResponse(ajax[request.path])

    if not request.path.endswith("/"):
        return d.HttpResponseRedirect(request.path + "/")

    raise d.Http404("File not found.")

# TODO:
#
#   this is for prototype only
#
#   once prototype looks okay and user wants to "upgrade" to proper django
#   project (importd based), for example to write custom models, user needs an
#   app.py that will have all the features, but will allow user to add apps and
#   change settings etc.
#
#   there should be a command djangothis --app[=app] that creates appropriate
#   app.py in the current folder (if it does not exists, complains if it does)

if __name__ == "__main__":
    d.main()
