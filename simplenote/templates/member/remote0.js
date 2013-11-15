// Simply get the current text which is selected (mostly by using mouse)
function getSelectedText() {
    var selection = '';
    if (window.getSelection) {
        selection = window.getSelection();
    } else if (document.selection) {
        selection = document.selection.createRange();
    }
    return selection;
}

function remoteSaveText(method, url, postbody, completionFn, errorFn)
{
    try {
        if (window.XDomainRequest) {
            var xdr = new XDomainRequest();
            if (! xdr) throw(0);
            xdr.onerror = errorFn;
            xdr.ontimeout = errorFn;
            xdr.onprogress = function(){};
            xdr.onload = function(){ completionFn(xdr.responseText); };
            xdr.open(method, url);
            xdr.send(postbody);
        } else if (window.XMLHttpRequest) {
            var x = new XMLHttpRequest();
            x.onreadystatechange = function() {
                try { 
                    if (x.readyState != 4) return;
                    if (x.status != 200) throw(0);
                    completionFn(x.responseText);
                } catch (e) { errorFn(); }
            }
            x.open(method, url, true);
            x.setRequestHeader("Content-type","application/x-www-form-urlencoded; charset=UTF-8");
            x.send(postbody);
        } else {
            errorFn();
        }
    } catch (e) { errorFn(); }
}

// Simply show out some messages, should be improved
function justNotify(message) 
{
    message = (typeof message == 'undefined' ? 'Bad thing happened' : message);
    alert(message);
}

// create new note or combine
var note_id = '{{ note_id }}';
var user_id = '{{ user_id }}';
// Send selected info out
var go_data = '';
//go_data = 'selection=' + getSelectedText();
go_data = 'selection=' + encodeURIComponent(getSelectedText());
go_data += '&source=' + document.location;
go_data += '&title=' + encodeURIComponent(document.title);
go_data += '&nid=' + encodeURIComponent(note_id);
go_data += '&user_id=' + encodeURIComponent(user_id);
remoteSaveText('POST', 
               'http://{{ site_domain }}/member/radd/{{ import_key }}', 
               go_data, 
               justNotify, 
               justNotify);
