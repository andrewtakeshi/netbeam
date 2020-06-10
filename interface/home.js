function formLogger(form)
{
    var text = "";
    for (var i = 0; i < form.length; i++)
    {
        if (form.elements[i].tagName != "BUTTON")
        {
            text += form.elements[i].name + ": " + form.elements[i].value + "\n";
        }
    }
    console.log(text);
}

function resetForms()
{
    var forms = $("form");
    for (var i = 0; i < forms.length; i++)
    {
        forms[i].reset();
    }
}

