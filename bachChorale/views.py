from django.shortcuts import render
from django.http import JsonResponse
import json
import os
import io
import matplotlib
from music21 import *
from .constants import *
from .scripts import *

matplotlib.use('SVG')# sets default graph's to svg format

# Create your views here.
def index(request):
    return render(request, "bachChorale/index.html", {
        "chorals": chorals,
        "plots": plotsKey,
        "analysis": analysisKey
    })

def getChorale(request):
    if request.method != "POST":
        return JsonResponse({"msg": "POST request required."}, status=400)
    try:
        data = json.loads(request.body)
        index = data.get("index")
        file = os.path.join('media/bachChorale/corpus', chorals[int(index)] + ".musicxml")
        file.replace(os.path.sep, '/')
        return JsonResponse({"file":file}, status=200)
    except:
        return JsonResponse({"msg": "Server error."}, status=400)

def getPlots(request, plot, index):
    if request.method != "GET":
        return JsonResponse({"msg": "GET request required."}, status=400)
    if not index:
        return JsonResponse({"msg": "Incomplete index data."}, status=400)

    try:
        file = os.path.join('media/bachChorale/corpus', chorals[index] + ".musicxml")
        score = converter.parse(file)
        plot_function = getattr(graph.plot, plotsValue[plot], None)
        if plot_function is not None and callable(plot_function):
            svg = plot_function(score)
        else:
            return JsonResponse({"msg": "Incomplete plot data."}, status=400)
        buffer = io.BytesIO()
        svg.doneAction = None
        svg.title = plotsValue[plot] + " " + chorals[index]
        svg.labelFontSize = 10
        svg.tickFontSize = 7
        svg.run()   
        svg.figure.savefig(buffer)
        path = "bachChorale/plots/" + chorals[index] + "-" + str(plot) + ".png"
        newfile = os.path.join('media',path).replace(os.path.sep, '/')
        svg.figure.savefig(fname=newfile, format="png")
        legend = ""
        if hasattr(svg, '_getLegend'):
            buffer2 = io.BytesIO()
            legend = svg._getLegend()
            legend.process()
            legend.figure.savefig(buffer2)
            legend = buffer2.getvalue().decode('UTF-8')
        svg = buffer.getvalue().decode('UTF-8')
        return JsonResponse({'svg':[svg, legend], 'file':newfile}, status=200)
    except:
        return JsonResponse({"msg": "Server error."}, status=400)
    
def getAnalysis(request, analysis, index):
    if request.method != "GET":
        return JsonResponse({"msg": "GET request required."}, status=400)
    if not index:
        return JsonResponse({"msg": "Incomplete index data."}, status=400)
    try:
        #search if file already exists!!
        file = os.path.join('media/bachChorale/corpus', chorals[index] + ".musicxml")
        score = converter.parse(file)
        analysis_function = globals().get(analysisValue[analysis])
        if analysis_function is not None and callable(analysis_function):
            newscore = analysis_function(score)
        else:
            return JsonResponse({"msg": "Incomplete analysis data."}, status=400)
        path = "bachChorale/analysis/" + chorals[index] + "-" + str(analysis) + ".musicxml"
        newfile = os.path.join('media',path).replace(os.path.sep, '/')
        newscore.write(fp=newfile)
        return JsonResponse({'file':newfile}, status=200) 
    except:
        return JsonResponse({"msg": "Server error."}, status=400)

def getSearch():
    return None