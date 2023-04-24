from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect
from django import forms
import markdown
import random
from . import util

class NewPageForm(forms.Form):
    title = forms.CharField(label="Title")
    markdown = forms.CharField(widget=forms.Textarea, label=("Markdown"))


class EditPageForm(forms.Form):
    title = forms.CharField(widget=forms.HiddenInput())
    markdown = forms.CharField(widget=forms.Textarea)
    
def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry(request, entry):
    entry_text = util.get_entry(entry)
    if entry_text == None:
        entry_text = "Error: Requested page not found."
   
    html = markdown.markdown(entry_text)
    #make title match what is saved for reference
    entries = util.list_entries()
    for item in entries:
        if item.upper() == entry.upper:
            entry = item

    
    return render(request, "encyclopedia/entry.html", {
        "title":entry,
        "entry_text":html
    })

    
def search(request):
    #get form input
    if request.method == "POST":
        form_response = request.POST
        search_term = form_response["q"]
        #check list of entries
        entries = util.list_entries()

        partial_matches = []

        # check if search term is in list of entries
        for item in entries:
            if search_term.upper() == item.upper():
                #convert search term to same form as list entry
                search_term = item
                print(item)
                return entry(request, search_term)
            
            # check if search term is a substring
            elif search_term.upper() in item.upper():
                partial_matches.append(item)

        # return search page showing multiple links if substring has any matches.
        if len(partial_matches) > 0:
            return render(request, "encyclopedia/search.html",{
                    "partial_matches":partial_matches
                })

        # if no matches return to home
        else:
            return HttpResponseRedirect(reverse("index"))

def new_page(request):
    if request.method == "POST":
        # Take in data user submitted as form
        form = NewPageForm(request.POST)
        # check if form data is valid - server side
        if form.is_valid():
            # isolate title from cleaned version of data
            title = form.cleaned_data["title"]
            #check if new title exists already
            entries = util.list_entries()
            for item in entries:
                if item.upper() == title.upper():
                    #rerender existing form data with an additional error message at top of page
                    return render(request, "encyclopedia/new_page.html", {
                        "error":"Error: Encyclopedia entry already exists with this name. Please choose a different one.",
                        "form":form
                        })
            #if title not in list, create new page:
            util.save_entry(title, form.cleaned_data["markdown"])
            return entry(request, title)

    else:
        return render(request, "encyclopedia/new_page.html",
        {
            "form": NewPageForm()
        })

def random_page(request):
    entries = util.list_entries()
    n = random.randint(0, len(entries))
    return entry(request, entries[n-1])


def edit_page(request, title):
    if request.method == "POST":
        form = EditPageForm(request.POST)
        if form.is_valid():
            markdown = form.cleaned_data["markdown"]
            #determine title form form as not in edit_page when route accessed by post
            title = form.cleaned_data["title"]
            util.save_entry(title, markdown)
            print(title)
            return entry(request, title)
    else:
        #get entry saved at edit_page title
        existing_markdown = util.get_entry(title)
        #populate form
        form = EditPageForm({'title':title, 'markdown':existing_markdown})
        return render(request, "encyclopedia/edit_page.html",{
            "form":form,
            "title":title
        })




        



            
        
                
            
    
        





    


