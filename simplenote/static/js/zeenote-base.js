/*
 * Global variables
 */
var N_SYNC_TITLE = 1;       // sync title
var N_SYNC_CONTENT = 2;     // sync content
var N_LOAD_LIST = 3;        // load list of notes
var N_TRASH = 4;           // remove a note
var N_CREATE = 5;           // create new note
var N_SHARE = 6;           // create new note
var N_SEARCH = 7;           // search a note
var N_DONT_SHARE = 8;           // search a note
var N_ADD_TAG = 9           // add tags for a note
var N_LOAD_LIST_BY_TAG = 10           // add tags for a note
var N_REMOVE_TAG = 11      // remove a tag of a note
var N_LOAD_TRASH= 12      // load all trashs
var N_DELETE = 13         // delete a note
var N_RESTORE = 14         // retore a note
/* 
 * Standardize the calling of ajax 
 */
function stdajax(params)
{
    sdata = params['data'];
    surl  = params['url'];
    stype = params['type'];
    handler = params['handler'];
    // ping it
    $.ajax({
        type: stype,
        url: surl,
        data: sdata
        }).done(handler); }


