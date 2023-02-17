
function clickEvent(e) {
    e.preventDefault();
    $(e.target).tab('show');
}
function deleteEvent(e){
    e.preventDefault();
    const tabId = $(e.target).closest('a[data-toggle="tab"]').attr('href');
    const editorIndex = $(e.target).closest('li').index();
    const editor = editors[editorIndex];
    if (editor) {
        editors.splice(editorIndex, 1);
    }
    $(tabId).remove();
    $(e.target).closest('li').remove();
}

function doubleClickEvent(e){
    const $tabLi = $(e.target);
  const $tabTitleLink = $tabLi.closest('a[data-toggle="tab"]');
  const current = $tabTitleLink.text().trim().slice(0,-1).trim();
  const classes = $tabTitleLink.attr('class');
    const id = $tabTitleLink.attr('id');
    const $input = $('<div><input type="text" class="form-control"> ' +
                    '<button class="closeBtn" data-dismiss="tab" aria-label="Close"><span aria-hidden="true">&times;</span></button></div>');
  $input.on('focusout', function() {
      if ($(this).find('input').val()===''){
          $(this).find('input').val(current)
      }
      const $output = $('<button class="closeBtn" data-dismiss="tab" aria-label="Close"><span aria-hidden="true">&times;</span></button>');
        $tabTitleLink.empty();
       $tabTitleLink.text($(this).find('input').val());
       $tabTitleLink.append($output);
       $tabTitleLink.attr('class', classes).attr('id', id);
         $output.closest('li').on('click', function(event) {
            clickEvent(event);
        }).on('dblclick',function (event){
            doubleClickEvent(event);
        }).find('button[data-dismiss="tab"]').on('click', function(event) {
            deleteEvent(event);
        });

  });
  $tabTitleLink.empty().append($input);
  $input.find('input').focus();
}
$(function () {
  $('#add-tab-btn').click(function () {
      const id = 'tab' + counter
      //insert tab
      $('<li class="nav-item editorTab"><a class="nav-link" data-toggle="tab" href="#' + id + '" role="tab">' + "Editor" + counter + '' +
          '<button class="closeBtn" data-dismiss="tab" aria-label="Close"><span aria-hidden="true">&times;</span></button>' +
          '</a></li>').insertAfter('#codeEditor .nav-tabs li:last')
      .click(function(event) {
          clickEvent(event);
        })
          .on('dblclick',function (event){
              doubleClickEvent(event);
          })
        .find('button[data-dismiss="tab"]').on('click', function(event) {
            deleteEvent(event);
        });
      //insert tab content
      $('<div class="tab-pane" id="' + id + '" role="tabpanel"><div id='+'code'+counter+'></div></div>').insertAfter('#codeEditor .tab-content .tab-pane:last');
      const parent = '#code'+counter;
      editors.push(cm6.createEditor('',parent));
      $('#codeEditor .nav-tabs a[href="#' + id + '"]').tab('show');
      counter++;
    });
  $('#codeEditor .nav-tabs .editorTab').click(function (event){
          clickEvent(event);
  });
   $('#codeEditor .nav-tabs button[data-dismiss="tab"]').click(function (event){
       deleteEvent(event);
   });
   $('.editorTab').on('dblclick', function (e){
       doubleClickEvent(e);
   })
});